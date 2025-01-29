import sqlalchemy as db
import datetime
import json
import os


# config
CSV_FILE_NAME: str = "Kundendaten.csv"
CSV_SEPARATOR: str = ";"


# database globals
META = db.MetaData()
ENGINE: db.Engine = ...
INSPECTOR: db.Inspector = ...


CUSTOMER_DATA_EMP = db.Table(
    "customer_data", META,
    db.Column("id", db.INT, primary_key=True, autoincrement=True),
    db.Column("salutation", db.VARCHAR(32), nullable=True),
    db.Column("first_name", db.VARCHAR(255), nullable=False),
    db.Column("last_name", db.VARCHAR(255), nullable=False),
    db.Column("birthday", db.DATE, nullable=True),
    db.Column("street", db.VARCHAR(255), nullable=True),
    db.Column("postal_code", db.INT, nullable=True),
    db.Column("city", db.VARCHAR(255), nullable=True),
    db.Column("email", db.VARCHAR(255), nullable=True),
    # autoload_with=ENGINE
)


def check_create_table() -> None:
    """
    create the table if it doesn't exist
    """
    if "customer_data" not in INSPECTOR.get_table_names():
        META.create_all(ENGINE)


def check_insert_csv() -> None:
    """
    checks if the csv file data has already been inserted, if not, inserts
    """
    with ENGINE.connect() as connection:
        query = db.select(CUSTOMER_DATA_EMP).where(
            CUSTOMER_DATA_EMP.c.first_name == "Tommy",
            CUSTOMER_DATA_EMP.c.last_name == "Rabenstein"
        )

        results = connection.execute(query).fetchall()

        if len(results) > 1:
            return

        # entry not found, try to insert
        with open(
                os.path.join(os.path.dirname(__file__), "data", CSV_FILE_NAME),
                "r"
        ) as csv_file:
            for line in csv_file:
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
                    values["birthday"] = datetime.date.fromisoformat(
                        "-".join(line[4].split(".")[-1])  # revert date (1.12.2000 -> 2000-12-1)
                    )

                # remove all elements with no value
                for key, value in values.items():
                    if value is None:
                        values.pop(key)

                print(f"inserting: {json.dumps(values, indent=4)}")

                # insert into database
                connection.execute(db.insert(CUSTOMER_DATA_EMP).values(**values))


def main():
    """
    program entry point
    """
    global ENGINE, INSPECTOR

    # read username and password from ENV
    username = os.environ.get("DB_UNAME", "Nilusink")
    password = os.environ.get("DB_PASS", "12345678")

    # create database engine
    ENGINE = db.create_engine(
        f"mariadb+mariadbconnector://{username}:{password}@127.0.0.1:3306/customer_data"
    )
    INSPECTOR = db.inspect(ENGINE)

    # make sure the database and data entries exist
    check_create_table()
    check_insert_csv()

if __name__ == "__main__":
    main()
