import sqlite3
import csv

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

case_reports_csv = open(f"{DATA_PATH}/virus/interim_infections.csv")
cases_reader = csv.DictReader(case_reports_csv)

airports_csv = open(f"{DATA_PATH}/flights/airports.csv")
airports_reader = csv.DictReader(airports_csv)

routes_csv = open(f"{DATA_PATH}/flights/routes.csv")
routes_reader = csv.DictReader(routes_csv)

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
    icao TEXT
)''')

c.execute('''CREATE TABLE routes(
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    departure_iata TEXT,
    arrival_iata TEXT,
    FOREIGN KEY (departure_iata) REFERENCES airports(iata),
    FOREIGN KEY (arrival_iata) REFERENCES airports(iata)
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
for row in cases_reader:
    c.execute("INSERT INTO cases (state, country, confirmed, died, recovered) VALUES (?, ?, ?, ?, ?)", (
        row["Province.State"], 
        row["Country.Region"], 
        row["Confirmed"], 
        row["Deaths"],
        row["Recovered"]))

for row in airports_reader:
    c.execute("INSERT INTO airports VALUES (?, ?, ?, ?, ?, ?)", (
        row["AIRPORT_ID"],
        row["NAME"],
        row["CITY"],
        row["COUNTRY"],
        row["IATA"],
        row["ICAO"]))

for row in airports_reader:
    c.execute("INSERT INTO routes (departure_iata, arrival_iata) VALUES (?, ?)", (
        row["DEP_ID"],
        row["ARR_ID"]))

conn.commit()
conn.close()

cities_csv.close()
countries_csv.close()
