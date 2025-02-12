"""
insert.py

reads data from a .csv file and transfers it into the database
if it does not already exist there

Author:
Niclas
"""
import mysql.connector as mariadb
import datetime
import os


# config
CSV_FILE_NAME: str = "Kundendaten.csv"
CSV_SEPARATOR: str = ";"


# database globals
CONNECTION = ...


def insert_row(
        connection,
        table_name: str = "customer_data",
        **values
) -> None:
    """
    insert existing rows into a table

    Args:
        connection: mysql connection
        table_name (str, optional): target table name.
            Defaults to `customer_data`.
    """
    query = (f"INSERT INTO {table_name} ("
             f"{', '.join(values.keys())}"
             f") VALUES ")
    vals = "("

    for value in values.values():
        # insert different data types correctly
        if isinstance(value, int):
            vals += f"{value}, "

        elif isinstance(value, datetime.date):
            vals += f"DATE '{value}', "

        # everything else is inserted as a string
        else:
            vals += f"'{value}', "

    else:
        # remove last ", "
        vals = vals[:-2]

    vals += ");"

    query += vals

    # print(f"Insert Query: \"{query}\"")

    # actually insert
    connection.execute(query)


def check_create_table() -> None:
    """
    create the table if it doesn't exist
    """
    # check if the table exists
    c = CONNECTION.cursor()
    c.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema = DATABASE() "
        "AND table_name = \"customer_data\"",
    )

    if c.fetchone()[0] == 0:
        print("table doesn't exist yet")
        c.execute("""create table customer_data
(
    id          int auto_increment
        primary key,
    salutation  varchar(32)  not null,
    first_name  varchar(255) not null,
    last_name   varchar(255) not null,
    birthday    date,
    street      varchar(255),
    postal_code int,
    city        varchar(255),
    email       varchar(255)
);
""")
        CONNECTION.commit()


def check_insert_csv() -> None:
    """
    checks if the csv file data has already been inserted, if not, inserts
    """
    c = CONNECTION.cursor()
    c.execute(
        "SELECT * FROM customer_data "
        "WHERE first_name=\"Tommy\" "
        "AND last_name=\"Rabenstein\";"
    )
    results = c.fetchall()

    if len(results) > 0:
        print("data already exists")
        return

    # entry not found, try to insert
    print("data not found, inserting")
    with open(
            os.path.join(
                os.path.dirname(__file__),
                "data",
                CSV_FILE_NAME
            ),
            "r"
    ) as csv_file:
        for n, line in enumerate(csv_file):

            # skip first line
            if n == 0:
                continue

            line = line.split(";")

            values = {
                "id": int(line[0]),
                "salutation": line[1],
                "first_name": line[2],
                "last_name": line[3],
                "street": line[5],
                "postal_code": int(line[6]) if line[6] else None,
                "city": line[7],
                "email": line[8]
            }

            # if existent, convert birthday to date and insert
            if line[4]:
                # revert date (1.12.2000 -> 2000-12-1)
                values["birthday"] = datetime.date.fromisoformat(
                    "-".join(line[4].split(".")[::-1])
                )

            # remove all elements with no value
            for key, value in values.copy().items():
                if value is None or value == "":
                    values.pop(key)

            # insert into database
            insert_row(connection=c, **values)

    CONNECTION.commit()
    print("data inserted")


def main() -> None:
    """
    program entry point
    """
    global CONNECTION

    # read username and password from ENV
    username = os.environ.get("DB_UNAME", "nilusink")
    password = os.environ.get("DB_PASS", "12345678")

    # create database engine
    CONNECTION = mariadb.connect(
        db='company',
        user=username,
        passwd=password,
        host='localhost'
    )

    # make sure the database and data entries exist
    check_create_table()
    check_insert_csv()


if __name__ == "__main__":
    main()
