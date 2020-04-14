import sqlite3
import numpy as np
import pandas as pd
import random
import csv
import json
from scipy import stats
import statsmodels.api as sm
from statsmodels.tools import eval_measures
import statsmodels.formula.api as smf
from datetime import date
import pprint


def pressure_as_cases_per_pop_times_traffic_volume(*args):
	# TODO: Normalize this data!
	cases, pop, traffic = args
	return (cases / pop) * traffic


def calc_viral_pressure(*args):
	"""A flexible function for calculating the viral pressure on a given country"""
	return pressure_as_cases_per_pop_times_traffic_volume(*args)

def parse_row(row):
	"""Parses a row of connectedness data into python data types"""
	# month, day, year = row[5].split("/")
	# year = int("20" + year)
	# date(year, int(month), int(day))
	new_row = [row[0], int(row[1]), row[2], int(row[3]), int(row[4]), row[5]]
	return new_row

def get_connectedness_data(db_location):
	"""
	Pulls connectedness data from the database then calculates the viral pressure on each node
	"""
	conn = sqlite3.connect(db_location)
	c = conn.cursor()
	connectedness_query = """
	select
		connections.arrival_country,
		connections.passengers,
		case_data.country,
		case_data.population,
		case_data.confirmed,
		case_data.date
	from (
		select *,
			(
				select airports.country
				from airports
				where airports.iata = departure_code
			) as departure_country,
			(
				select airports.country
				from airports
				where airports.iata = arrival_code
			) as arrival_country
		from (
			select t.departure_code, t.arrival_code, t.passengers
			from traffic as t
			join airports as a
			on a.iata = t.departure_code
		)
	) as connections
	join (
		select ca.date, ca.country, ca.confirmed, co.population
		from cases as ca
		join countries as co
		on ca.country = co.name
	) as case_data
	on case_data.country = connections.departure_country
	where arrival_country != departure_country -- only international flights
	"""
	# Join case data and route data on country
	# We now have a time series of cases of over time matched with
	# flight route data. This is our baseline dataset.
	# Probably create a pandas dataframe here
	connectedness_data = [parse_row(row) for row in c.execute(connectedness_query)]
	"""
	connectedness_data = [
		hub_country :: String # This is the hub country
		spoke_passengers :: Integer # Total number of passengers on route in last year
		spoke_country :: String, # This is a spoke country
		spoke_pop :: Integer, # This is the population of the spoke
		spoke_confirmed_cases :: Integer, # Number of confirmed cases in spoke on date
		date :: String, # Date of case data
	]
	"""
	countries_query = "select name from countries;"
	countries = [row[0] for row in c.execute(countries_query)]

	# Set up an accumulator for structuring data
	acc = {}
	with open("data/virus/case_series.json") as cases_json:
		_, dates = json.load(cases_json)["labels"]
	for date in dates:
		acc[date] = {}
		for country in countries:
			# accumulate viral pressure here
			acc[date][country] =  0
	# Populate acc
	# collect all data points from connectedness data
	for row in connectedness_data:
		hub_country, passengers, spoke_country, spoke_pop, spoke_confirmed_cases, cur_date = row
		acc_viral_pressure = acc[cur_date][hub_country]
		cur_viral_pressure = calc_viral_pressure(spoke_confirmed_cases, spoke_pop, passengers)
		acc[cur_date][hub_country] = acc_viral_pressure + cur_viral_pressure
		acc[cur_date][hub_country]
	# print(acc["4/9/20"]["United States"])
	# Use acc to calculate rows of X
	# Transform acc back to a list
	# NOTE: Feel free to get rid of this and work directly with acc
	X = []
	for date in dates:
		for country in countries:
			viral_pressure = acc[date][country]
			X.append((date, country, viral_pressure))
	return X


def get_case_data(db_location):
	"""
	Pulls case data from the database
	"""
	conn = sqlite3.connect(db_location)
	c = conn.cursor()
	case_query = """
	select country, date, confirmed
	from cases
	order by country, date;
	"""
	# 
	# Probably create a pandas dataframe here
	case_data = [row for row in c.execute(case_query)]
	"""
	case_data = {
		country :: String,
		date :: date,
		number of confirmed cases :: Integer
	}
	"""
	# there's definitely a better way to do this

	y = []
	"""
	y = {
		country :: String,
		date :: String,
		days until/since (positive/negative) first case :: Integer
	}
	"""
	# days since infection; negative
	prev_country = case_data[0][0]
	days = 0
	for row in case_data:
		if (prev_country != row[0]):
			prev_country = row[0]
			days = 0
		if row[2] > 0:
			days -= 1
		new_row = [row[0], row[1], days]
		y.append(new_row)

	# days until infection; positive
	prev_country = y[-1][0]
	days = 0
	i = len(y) - 1
	while i >= 0:
		if (prev_country != y[i][0]):
			prev_country = y[i][0]
			days = 0
		if y[i][2] > -1:
			y[i][2] = days
			days += 1
		i -= 1

	return y

def pair_Xy(X, y):
	y_paired = []
	X_paired = []
	for X_row in X:
		for y_row in y:
			if X_row[2] == y_row[0] and X_row[-1] == y_row[1]:
				X_row.pop(2)
				y_paired.append(y_row[2])
				X_paired.append(X_row[:-1])
				break
	return X_paired, y_paired

# Goal data spec for running regressions
# X_all = [Date :: Date, Country :: String, Viral pressure :: Float]
# Y_all = [Date :: Date, Country :: String, Days to infection :: Integer]
# Train test split on countries X_i

# Evan's TODO:
# 1. Wire up the regression
# 2. Double check code for gettting Y_all
# 3. Test on fake data

# Quinn's TODO:
# 1. Get connectedness data

# NOTE: Everything below here is just copy-pasted from multiple-regression.py
def train_test_split(x, y, test_pct):
	"""input:
	x: list of x values, y: list of independent values, test_pct: percentage of the data that is testing data=0.2.

	output: x_train, x_test, y_train, y_test lists
	"""
	
	#TODO: Split the features X and the labels y into x_train, x_test and y_train, y_test as specified by test_pct. 
	#You can re-use code from part I.
	# Turn this into a numpy
	test_size = round(len(x) * test_pct)
	test_indices = random.sample(range(len(x)), test_size)
	train_indices = list(set(range(len(x))).difference(set(test_indices)))
	x_test = np.array([x[i] for i in test_indices])
	x_train = np.array([x[i] for i in train_indices])
	y_test = np.array([y[i] for i in test_indices])
	y_train = np.array([y[i] for i in train_indices])
	return (x_train, x_test, y_train, y_test)

if __name__ == "__main__":
	p = 0.2
	X = get_connectedness_data("data.db")
	y = get_case_data("data.db")
	# TODO: Collect y
	pp = pprint.PrettyPrinter(indent=4)
	# Print out all countries for each date where viral pressure is not 0
	pp.pprint([x for x in X if x[2] != 0])

	# (X, y) = pair_Xy(X, y)


	# # Use train test split to split data into x_train, x_test, y_train, y_test #
	# (x_train, x_test, y_train, y_test) = train_test_split(X, y, p)
	# # print(type(x_train), type(x_test), type(y_train))

	# # Use StatsModels to create the Linear Model and Output R-squared
	# x_train = sm.add_constant(x_train) # add a constant column to be intercept
	# model = sm.OLS(y_train, x_train)
	# results = model.fit()
	# print(results.summary())

	# # Prints out a report containing
	# # R-squared, test MSE & train MSE
	# print(f"R2: {results.rsquared}")
	# training_mse = eval_measures.mse(y_train, results.predict(x_train))
	# print(f"Training MSE: {training_mse}")
	# x_test = sm.add_constant(x_test)
	# predicted_y_test = results.predict(x_test)
	# testing_mse = eval_measures.mse(y_test, predicted_y_test)
	# print(f"Testing MSE: {testing_mse}")
	# exit(0)
