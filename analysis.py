import sqlite3
import numpy as np
import pandas as pd
import random
import csv
from scipy import stats
import statsmodels.api as sm
from statsmodels.tools import eval_measures
import statsmodels.formula.api as smf


def pressure_as_cases_per_pop_times_traffic_volume(
	incoming_cases,
	incoming_traffic,
	incoming_populations):
	return sum([cases / pop for cases, pop in zip(incoming_cases, incoming_populations)])


def viral_pressure(*args):
	"""A flexible function for calculating the viral pressure on a given country"""
	return pressure_as_cases_per_pop_times_traffic_volume(*args)

def get_connectedness_data(db_location):
	"""
	Pulls connectedness data from the database then calculates the viral pressure on each node
	"""
	conn = sqlite3.connect(db_location)
	c = conn.cursor()
	connectedness_query = """
	select
		count(),
		sum(connections.passengers),
		connections.arrival_country,
		group_concat(case_data.country, ","),
		group_concat(case_data.population, ","),
		group_concat(case_data.confirmed, ","),
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
	group by connections.arrival_country;
	"""
	# Join case data and route data on country
	# We now have a time series of cases of over time matched with
	# flight route data. This is our baseline dataset.
	# Probably create a pandas dataframe here
	connectedness_data = [row for row in c.execute(connectedness_query)]
	"""
	connectedness_data = {
		number of incoming routes :: Integer,
		country :: String
		number of incoming passengers :: Integer,
		# TODO: Need to add a list of incoming passengers here
		list of incoming countries :: String (comma separated)
		list of incoming populations :: String (comma separated)
		list of case data :: String (comma separated)
		date :: String
	}
	"""

	# Compute case rates by dividing case counts by population
	# We may want to experiment during the regression step with
	# different ways of generating this number.
	# Now we at least have something we can do regression on
	X = []
	for row in connectedness_data:
		incoming_countries = row[3].split(",")
		incoming_populations = [int(num) for num in row[4].split(",")]
		incoming_cases = [int(case) for case in row[5].split(",")]
		# TODO: This is wrong!!
		viral_pressure = viral_pressure(incoming_cases, incoming_populations)
		new_row = [row[0], row[1], row[2], incoming_countries, incoming_populations, incoming_cases, viral_pressure]
		X.append(new_row)
	return X

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
	X = get_connectedness_data("data.db")
	# TODO: Collect y

	# Use train test split to split data into x_train, x_test, y_train, y_test #
	(x_train, x_test, y_train, y_test) = train_test_split(X, y, p)
	# print(type(x_train), type(x_test), type(y_train))

	# Use StatsModels to create the Linear Model and Output R-squared
	x_train = sm.add_constant(x_train) # add a constant column to be intercept
	model = sm.OLS(y_train, x_train)
	results = model.fit()
	print(results.summary())

	# Prints out a report containing
	# R-squared, test MSE & train MSE
	print(f"R2: {results.rsquared}")
	training_mse = eval_measures.mse(y_train, results.predict(x_train))
	print(f"Training MSE: {training_mse}")
	x_test = sm.add_constant(x_test)
	predicted_y_test = results.predict(x_test)
	testing_mse = eval_measures.mse(y_test, predicted_y_test)
	print(f"Testing MSE: {testing_mse}")
	exit(0)
