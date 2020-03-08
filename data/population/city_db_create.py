import sqlite3
import csv

cities_csv = open("./city-populations.csv", encoding = "ISO-8859-1")
city_reader = csv.DictReader(cities_csv)

states_csv = open("./state-populations.csv", encoding = "us-ascii")
state_reader = csv.DictReader(states_csv)

countries_csv = open("./country-populations.csv", encoding="us-ascii")
country_reader = csv.DictReader(countries_csv)

# Create connection to database
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Delete tables if they exist
c.execute('DROP TABLE IF EXISTS "cities";')
c.execute('DROP TABLE IF EXISTS "states";')
c.execute('DROP TABLE IF EXISTS "countries";')

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

conn.commit()

for row in city_reader:
    c.execute("INSERT INTO cities (name, state, population) VALUES (?, ?, ?)", (
        row["NAME"], row["STNAME"], row["POPESTIMATE2018"]))

for row in state_reader:
    c.execute("INSERT INTO states VALUES (?, ?, ?)", (
        row["NAME"],
        "United States of America", 
        row["POPESTIMATE2018"]))

for row in country_reader:
    c.execute("INSERT INTO countries VALUES (?, ?, ?, ?, ?)", (
        row["Country"], 
        row["Year"], 
        row["Population"], 
        row["Area (sq. km.)"], 
        row["Density (persons per sq. km.)"]))

conn.commit()
conn.close()

cities_csv.close()
countries_csv.close()
