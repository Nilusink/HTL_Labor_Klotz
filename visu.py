"""
visu.py

Author:
Lilo
Niclas
Daniel
"""
from geopy.geocoders import Nominatim
import plotly.graph_objects as go
import mysql.connector as mariadb
from threading import Thread
import plotly.express as px
from dash import dcc, html
from datetime import date
from time import sleep
import pandas as pd
import json
import dash
import os


# read username and password from ENV
USERNAME = os.environ.get("DB_UNAME", "nilusink")
PASSWORD = os.environ.get("DB_PASS", "12345678")

# globals init
APP = dash.Dash(__name__)
GEOLOCATOR = Nominatim(user_agent="geo_plotting")
data = []


# helper functions
def calculate_age(birth_date: date) -> int:
    """
    calculate an age based on a birthday
    :param birth_date:
    :return:
    """
    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day)
        < (birth_date.month, birth_date.day)
    )
    return age


def get_lat_lon(address: str) -> tuple[float, float] | None:
    """
    convert a string address to latitude and longitude
    """
    location = GEOLOCATOR.geocode(address)
    return (
        location.latitude,
        location.longitude
    ) if location else None


def geolocate_in_background(addresses) -> None:
    """
    background thread converting addresses to coordinates
    """
    global data

    for i, address in enumerate(addresses):
        address, name = address.split(";")

        # check if already located
        for location in data:
            if location["Address"] == address:
                break

        # not located yet, request from API
        else:
            while True:
                print(f"\rLocating: {address}")
                print(f"{i}/{len(addresses)}", end="")

                # try to request address coords from API,
                # if fail wait for 20 secs
                try:
                    coords = get_lat_lon(address)

                except Exception:
                    print("timeout, waiting 20 seconds")
                    sleep(20)
                    continue

                # check if coords were found
                if coords is None:
                    print(f"\rfailed to locate {address}")
                    print(f"{i + 1}/{len(addresses)}", end="")
                    continue

                print(f"\r{address} is at {coords[0]}, {coords[1]}")
                print(f"{i + 1}/{len(addresses)}", end="")

                # append coords to dataset
                data.append({
                    "Address": address,
                    "Name": name,
                    "Latitude": coords[0],
                    "Longitude": coords[1],
                })

                # update json every time
                with open(f"location_data.json", "w") as outfile:
                    json.dump(data, outfile)

                # continue with next address
                break


def main() -> None:
    """
    program entry point
    """
    global data

    # init database
    conn = mariadb.connect(
        db='company',
        user=USERNAME,
        passwd=PASSWORD,
        host='localhost'
    )

    cursor = conn.cursor()

    # request data
    cursor.execute("SELECT COUNT(*) FROM customer_data")
    total_columns = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM customer_data "
        "WHERE salutation = \"Frau\""
    )
    value_frauen = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM customer_data "
        "WHERE salutation = \"Herr\""
    )
    value_herren = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM customer_data "
        "WHERE salutation = \"k.A.\""
    )
    value_divers = cursor.fetchone()[0]

    cursor.execute("SELECT birthday FROM customer_data")
    birthdays = cursor.fetchall()

    cursor.execute(
        "SELECT COUNT(*) FROM customer_data "
        "WHERE EMail is NULL OR Email = \"\n\""
    )
    not_provided = cursor.fetchone()[0]

    cursor.execute(
        "SELECT postal_code, city, first_name, last_name "
        "FROM customer_data"
    )
    user_data = cursor.fetchall()

    # Gender Pie Graph
    labels = ['Weiblich', 'Männlich', 'keine Angabe']
    values = [value_frauen, value_herren, value_divers]

    gender_fig = go.Figure(
        data=[go.Pie(labels=labels, values=values)]
    )

    # Age graph
    ages = [
        calculate_age(birthday)
        for (birthday, ) in birthdays if birthday is not None
    ]

    ## calculate below 30, 30-60 and 60+
    below_30 = len([age for age in ages if age < 30])
    between = len([age for age in ages if 30 <= age <= 60])
    over_60 = len([age for age in ages if age > 60])

    age_values = [below_30, between, over_60]
    age_fig = go.Figure(data=[go.Pie(
        labels=["below 30", "30-60", "over 60"],
        values=age_values
    )])

    # how many provided emails?
    email_values = [not_provided, total_columns - not_provided]
    email_fig = go.Figure(data=[go.Pie(
        labels=["not provided", "provided"],
        values=email_values
    )])

    # addresses on map
    addresses = [f"{s} {c}, germany;{f} {l}" for s, c, f, l in user_data]

    ## try to load location data
    if os.path.isfile("location_data.json"):
        data = json.load(open("location_data.json"))

    ## only create map if data exists
    if len(data) != 0:
        # Convert to DataFrame
        df = pd.DataFrame(data)

        fig = px.scatter_map(
            df,
            lat="Latitude",
            lon="Longitude",
            hover_name="Name",
            hover_data=["Address", "Latitude", "Longitude"],
            zoom=5,
        )

    # Web-app
    APP.layout = html.Div(
        [
            html.H1("Customer Database Visualization"),
            html.H2("Gender Distribution"),
            dcc.Graph(figure=gender_fig),
            html.H2("Age Distribution"),
            dcc.Graph(figure=age_fig),
            html.H2("User Provided an E-mail?"),
            dcc.Graph(figure=email_fig),
            dcc.Graph(
                figure=fig,
                style={"height": "50vw"}
            ) if len(data) != 0 else None,
        ],
        style={
            "textAlign": "center",
        }
    )

    # start threads and web app
    Thread(
        target=geolocate_in_background,
        args=[addresses]
    ).start()
    APP.run_server(debug=True)


# Run the Dash app
if __name__ == '__main__':
    main()
