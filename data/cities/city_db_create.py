import sqlite3
import csv

with open("city-populations.csv") as cities_csv:
    city_reader = csv.DictReader(cities_csv)

# with open("PEP_2018_PEPANNRSIP.US12A.csv") as states_csv:
#     state_reader = csv.DictReader(cities_csv)

with open("country-populations.csv") as countries_csv:
    country_reader = csv.DictReader(cities_csv)

# Create connection to database
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Delete tables if they exist
c.execute('DROP TABLE IF EXISTS "cities";')
c.execute('DROP TABLE IF EXISTS "states";')
c.execute('DROP TABLE IF EXISTS "countries";')

#TODO: Create tables in the database and add data to it. REMEMBER TO COMMIT

# Useful column names: NAME,STNAME,POPESTIMATE2018
c.execute('''CREATE TABLE cities (
    name text NOT NULL, 
    state text NOT NULL, 
    population INTEGER NOT NULL
    PRIMARY KEY (name)
    FOREIGN KEY (state) REFERENCES states(name)
)''')

c.execute('''CREATE TABLE states (
    name text NOT NULL, 
    population INTEGER NOT NULL, 
    PRIMARY KEY (name)
)''')

# area in square kilometers
# density in persons per square kilometer
# Column names: Country,Year,Population,"Area (sq. km.)","Density (persons per sq. km.)"
c.execute('''CREATE TABLE countries (
    name text NOT NULL,
    year INTEGER,
    population INTEGER NOT NULL,
    area REAL NOT NULL,
    density REAL NOT NULL,
    PRIMARY KEY (name)
)''')

conn.commit()

for row in city_reader:
    c.execute("INSERT INTO cities VALUES (?, ?, ?)", (
        row["NAME"], row["STNAME"], row["POPESTIMATE2018"]))

for row in country_reader:
    c.execute("INSERT INTO companies VALUES (?, ?, ?, ?, ?)", (
        row["Country"], 
        row["Year"], 
        row["Population"], 
        row["Area (sq. km.)"], 
        row["Density (persons per sq. km.)"))

conn.commit()
conn.close()
