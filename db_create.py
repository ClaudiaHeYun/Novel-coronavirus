import sqlite3
import csv
import datetime
import json

DATA_PATH = "data"

cities_csv = open(f"{DATA_PATH}/population/us-cities-populations.csv", encoding = "ISO-8859-1")
city_reader = csv.DictReader(cities_csv)

countries_csv = open(f"{DATA_PATH}/population/country-populations-2018.csv", encoding="us-ascii")
country_reader = csv.DictReader(countries_csv)

states_csv = open(f"{DATA_PATH}/population/us-states-populations-2018.csv", encoding = "us-ascii")
us_state_reader = csv.DictReader(states_csv)

canada_csv = open(f"{DATA_PATH}/population/canada-provinces-2016.csv")
canada_reader = csv.DictReader(canada_csv)

australia_csv = open(f"{DATA_PATH}/population/australia-populations-2018.csv")
australia_reader = csv.DictReader(australia_csv)

china_csv = open(f"{DATA_PATH}/population/china-populations-2018.csv")
china_reader = csv.DictReader(china_csv)

# case_reports_csv = open(f"{DATA_PATH}/virus/infections.csv")
# cases_reader = csv.DictReader(case_reports_csv)
case_reports_file = open(f"{DATA_PATH}/virus/case_series.json")
cases_json = json.load(case_reports_file)

airports_csv = open(f"{DATA_PATH}/flights/airports.csv")
airports_reader = csv.DictReader(airports_csv)

routes_csv = open(f"{DATA_PATH}/flights/routes.csv")
routes_reader = csv.DictReader(routes_csv)

traffic_csv = open(f"{DATA_PATH}/flights/top-100-routes.csv")
traffic_reader = csv.DictReader(traffic_csv)

# Create connection to database
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Delete tables if they exist
c.execute('DROP TABLE IF EXISTS "cities";')
c.execute('DROP TABLE IF EXISTS "states";')
c.execute('DROP TABLE IF EXISTS "countries";')
c.execute('DROP TABLE IF EXISTS "cases";')
c.execute('DROP TABLE IF EXISTS "airports";')
c.execute('DROP TABLE IF EXISTS "routes";')
c.execute('DROP TABLE IF EXISTS "traffic";')

#TODO: Create tables in the database and add data to it. REMEMBER TO COMMIT

# Useful column names: NAME,STNAME,POPESTIMATE2018
c.execute('''CREATE TABLE cities(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    state TEXT NOT NULL, 
    population INTEGER NOT NULL,
    FOREIGN KEY (state) REFERENCES states(name)
)''')

c.execute('''CREATE TABLE states(
    name TEXT NOT NULL,
    abbreviation TEXT,
    country TEXT NOT NULL,
    population INTEGER NOT NULL,
    PRIMARY KEY (name)
)''')

# area in square kilometers
# density in persons per square kilometer
# Column names: Country,Year,Population,"Area (sq. km.)","Density (persons per sq. km.)"
c.execute('''CREATE TABLE countries(
    name TEXT NOT NULL,
    year INTEGER,
    population INTEGER NOT NULL,
    area REAL NOT NULL,
    density REAL NOT NULL,
    PRIMARY KEY (name)
)''')

c.execute('''CREATE TABLE cases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    state TEXT,
    country TEXT,
    confirmed INTEGER,
    deaths INTEGER,
    recovered INTEGER
)''')

c.execute('''CREATE TABLE airports(
    airport_id INTEGER PRIMARY KEY,
    name TEXT,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    iata TEXT NOT NULL,
    icao TEXT NOT NULL
)''')

c.execute('''CREATE TABLE routes(
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    departure_code TEXT,
    arrival_code TEXT,
    FOREIGN KEY (departure_code) REFERENCES airports(iata),
    FOREIGN KEY (arrival_code) REFERENCES airports(iata)
)''')

c.execute('''CREATE TABLE traffic (
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    departure_code TEXT,
    arrival_code TEXT,
    passengers INTEGER,
    flights INTEGER,
    FOREIGN KEY (departure_code) REFERENCES airports(iata),
    FOREIGN KEY (arrival_code) REFERENCES airports(iata)
)''')

conn.commit()

for row in city_reader:
    c.execute("INSERT INTO cities (name, state, population) VALUES (?, ?, ?)", (
        row["NAME"], row["STNAME"], row["POPESTIMATE2018"]))

for row in us_state_reader:
    c.execute("INSERT INTO states (name, abbreviation, country, population) VALUES (?, ?, ?, ?)", (
        row["NAME"],
        row["ABBREV"],
        "United States of America", 
        row["POPESTIMATE2018"]))

for row in canada_reader:
    c.execute("INSERT INTO states (name, country, population) VALUES (?, ?, ?)", (
        row["Geographic name"],
        "Canada", 
        row["Population, 2016"]))

for row in australia_reader:
    c.execute("INSERT INTO states (name, country, population) VALUES (?, ?, ?)", (
        row["State"],
        "Australia", 
        row["Population"]))

for row in china_reader:
    c.execute("INSERT INTO states (name, country, population) VALUES (?, ?, ?)", (
        row["Region"],
        "China", 
        row["Population"]))

for row in country_reader:
    c.execute("INSERT INTO countries VALUES (?, ?, ?, ?, ?)", (
        row["Country"], 
        row["Year"], 
        row["Population"], 
        row["Area (sq. km.)"], 
        row["Density (persons per sq. km.)"]))

# TODO clean up US and UK names in order to join by foreign key
labels = cases_json["labels"]
print(labels)
for row in cases_json["countries"]:
    for date, daily_total in zip(labels[2], row[2]):
        m_d_y = date.split("/")
        year = "20" + m_d_y[-1]
        if len(m_d_y[0]) == 1:
            month = "0" + m_d_y[0]
        else:
            month = m_d_y
        if len(m_d_y[1]) == 1:
            day = "0" + m_d_y[1]
        else:
            day = m_d_y[1]
        YYYY_MM_DD = year + "-" + month + "-" + day
        c.execute("INSERT INTO cases (date, country, confirmed) VALUES (?, ?, ?)", (
            YYYY_MM_DD,
            row[1], 
            daily_total))

for row in airports_reader:
    # NOTE: IATA codes has \N when no code is known. There 1626 such records
    # NOTE: ICAO has one record with a \N
    c.execute("INSERT INTO airports VALUES (?, ?, ?, ?, ?, ?)", (
        row["AIRPORT_ID"],
        row["NAME"],
        row["CITY"],
        row["COUNTRY"],
        row["IATA"],
        row["ICAO"]))

for row in routes_reader:
    c.execute("INSERT INTO routes (departure_code, arrival_code) VALUES (?, ?)", (
        row["DEP"],
        row["ARR"]))

for row in traffic_reader:
    (dep, arr) = row["Route by code"].split("-")
    c.execute("INSERT INTO traffic (departure_code, arrival_code, passengers) VALUES (?, ?, ?)",(
        dep,
        arr,
        row["Passengers - 2017"]
    ))

conn.commit()
conn.close()

cities_csv.close()
countries_csv.close()
states_csv.close()
case_reports_file.close()
canada_csv.close()
china_csv.close()
routes_csv.close()
traffic_csv.close()
