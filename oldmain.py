#!/usr/bin/python3

# Turn on debug mode.
# import cgitb
# cgitb.enable()

# Print necessary headers.
print("Content-Type: text/html")
print()
print('<p style="color: blue;">')

# Connect to the database.
import mysql.connector as db
import os


username = os.environ.get("username", "nilusink")
password = os.environ.get("password", "12345678")

conn = db.connect(
    db='workplace',
    user=username,
    passwd=password,
    host='localhost')

c = conn.cursor()

def clear_data():
    try:
        c.execute("DELETE FROM employees;")

    except db.Error:
        return


def add_data(first_name, last_name):
    try:
        statement = "INSERT INTO employees (first_name,last_name) VALUES (%s, %s)"
        data = (first_name, last_name)
        c.execute(statement, data)
        conn.commit()
        print("Successfully added entry to database")

    except db.Error as e:
        print(f"Error adding entry to database: {e}")

def add_names() -> None:
    add_data("Luca", "Bombardelli")
    add_data("Luca", "Brecher")
    add_data("Berke", "Erdik")
    add_data("Marcel", "Hager")
    add_data("Luka", "Jandrić")
    add_data("Tobias", "Krismer")
    add_data("Dominik", "Lechner")
    add_data("Emanuel", "Mair")
    add_data("Leon", "Pezzei")
    add_data("Thomas", "Schmid")
    add_data("Lucas", "Tusch")

def get_data(last_name):
    try:
      statement = "SELECT first_name, last_name FROM employees WHERE last_name=%s"
      data = (last_name,)
      c.execute(statement, data)
      for (first_name, last_name) in c:
        print(f"Successfully retrieved {first_name}, {last_name}")

    except db.Error as e:
      print(f"Error retrieving entry from database: {e}")

def get_data2() -> None:
    try:
      statement = "SELECT first_name FROM employees WHERE NOT last_name=\"Doe\""
      c.execute(statement)
      for (first_name, ) in c:
        print(f"Successfully retrieved {first_name}")

    except db.Error as e:
      print(f"Error retrieving entry from database: {e}")


def get_data3() -> None:
    try:
        statement = "SELECT *  FROM employees WHERE first_name LIKE 'Lu%';"

        c.execute(statement)
        for (first_name, last_name) in c:
            print(f"Successfully retrieved {first_name} {last_name}")

    except db.Error as e:
      print(f"Error retrieving entry from database: {e}")

def main() -> None:
    clear_data()

    add_data("Kofi", "Doe")

    add_names()

    get_data3()

    conn.close()


if __name__ == "__main__":
    main()
