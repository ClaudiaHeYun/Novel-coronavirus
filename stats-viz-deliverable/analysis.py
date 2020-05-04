import sqlite3
import numpy as np
import pandas as pd
import random
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
from scipy import stats 
import statsmodels.api as sm
from statsmodels.tools import eval_measures
import statsmodels.formula.api as smf
from datetime import date
import pprint


DATA = "../data"

def pressure_as_cases_per_pop_times_traffic_volume(*args):
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
	Pulls connectedness data from the database
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
				join (select country from cases) as case_country
				on case_country.country = airports.country
				where airports.iata = departure_code
			) as departure_country,
			(
				select airports.country
				from airports
				join (select country from cases) as case_country
				on case_country.country = airports.country
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
	;
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
	return connectedness_data


def get_viral_pressure_data(connectedness_data, db_location):
	"""
	Meant to be chained together with get_connectedness_data. Takes the connectedness data and
	produces a time series of cases of over time matched with flight route data
	"""
	conn = sqlite3.connect(db_location)
	c = conn.cursor()
	countries_query = "select country from cases"
	countries = [row[0] for row in c.execute(countries_query)]
	conn.close()

	# Set up an accumulator for structuring data
	data = {}
	with open(f"{DATA}/virus/case_series.json") as cases_json:
		_, dates = json.load(cases_json)["labels"]
	for date in dates:
		data[date] = {}
		for country in countries:
			# accumulate viral pressure here
			data[date][country] =  0
	
	# Populate accumulator by collecting all data points from connectedness data
	for row in connectedness_data:
		hub_country, passengers, spoke_country, spoke_pop, spoke_confirmed_cases, cur_date = row
		acc_viral_pressure = data[cur_date][hub_country]
		cur_viral_pressure = calc_viral_pressure(spoke_confirmed_cases, spoke_pop, passengers)
		data[cur_date][hub_country] = acc_viral_pressure + cur_viral_pressure
		data[cur_date][hub_country]

	return data


def flatten_data(data):
	"""Flatten viral pressure data into an array of tuples"""
	conn = sqlite3.connect("../data.db")
	c = conn.cursor()
	countries_query = "select country from cases group by country;"
	countries = [row[0] for row in c.execute(countries_query)]
	conn.close()

	with open(f"{DATA}/virus/case_series.json") as cases_json:
		_, dates = json.load(cases_json)["labels"]
		# Use acc to calculate rows of X
	# Transform acc back to a list
	# NOTE: Feel free to get rid of this and work directly with acc
	X = []
	for date in dates:
		for country in countries:
			viral_pressure = data[date][country]
			X.append((country, date, viral_pressure))
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
	return case_data


def get_dates(db_location):
	"""
	Pulls data from the database
	"""
	conn = sqlite3.connect(db_location)
	c = conn.cursor()
	date_query = """
	select date
	from cases
	group by date
	order by date;
	"""
	dates = [row[0] for row in c.execute(date_query)]
	return dates


def process_y(case_data):
	"""Calculate days to first infection"""
	# TODO: Change this to not go negative
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

def add_previous_cases(X, case_data):
	# ordered_dates = get_dates("data.db")
	# print(ordered_dates)
	index = 1
	curr_country = X[0][0]
	while index < len(X):
		record = list(X[index])
		if (curr_country == X[index][0]):
			record.append(case_data[index-1][2])
			X[index] = record
			index += 1
		else:
			curr_country = X[index][0]
			X[index] = record
			index += 1
	return X

# def add_missing(countries, x_sorted, y, default):

# 	# caseless_countries = ['American Samoa']
# 	# extra_entries = []
# 	# for x in x_sorted:
# 	# 	matched = False
# 	# 	for y in y_sorted:
# 	# 		if (x[0] == y[0]):
# 	# 			matched = True
# 	# 			break
# 	# 	if not matched:
# 	# 		# print(x[0])
# 	# 		if not caseless_countries[-1] == x[0]:
# 	# 			caseless_countries.append(x[0])
# 	# 			print(x[0])
# 	# 		extra_entries.append(x)

# 	days = [y_sorted[0][1]]
# 	for row in y[1:]:
# 		if row[1] == days[0]:
# 			break
# 		else:
# 			days.append(row[1])

# 	print(days)
# 	for country in countries:
# 		for day in days:
# 			y.append([country, day, default])
# 	return y

# def get_days(sorted_country_day):
# 	days = [sorted[0][1]]
# 	for row in y[1:]:
# 		if row[1] == days[0]:
# 			break
# 		else:
# 			days.append(row[1])
# 	return len(days), days

def overall_viral_pressure_analysis(file_path, y):
	"""Run a regression over all countries over the whole timeline on viral pressure"""
	X = flatten_data(get_viral_pressure_data(get_connectedness_data(file_path), file_path))

	x_sorted = sorted(X, key=lambda x: x[1] + x[0])
	y_sorted = sorted(y, key=lambda x: x[1] + x[0])	
	x_sorted_pressure = [x[2] for x in x_sorted]
	y_sorted_days = [y[2] for y in y_sorted]

	plt.scatter(x_sorted_pressure, y_sorted_days)
	plt.ylabel("Days to infection")
	plt.xlabel("Viral pressure")
	plt.savefig("results/full_scatter.png")
	plt.clf()

	# Print out all countries for each date where viral pressure is not 0
	nonzero_x = [x for x in X if x[2] != 0]
	# print("Total rows in X:", len(X))
	# print("Total nonzero rows in X:", len(nonzero_x))
	# rows_sorted_by_pressure = sorted(nonzero_x, key=lambda x: x[2], reverse=True)
	# print("Top 10 rows by viral pressure:")
	# pp.pprint(rows_sorted_by_pressure[:10])

	plt.hist([x[2] for x in nonzero_x])
	plt.ylabel("Viral Pressure")
	plt.savefig("results/viral_pressure.png")

	# Use train test split to split data into x_train, x_test, y_train, y_test #
	# (x_train, x_test, y_train, y_test) = train_test_split(x_sorted_pressure, y_sorted_days, p)
	# print(type(x_train), type(x_test), type(y_train))

	# Use StatsModels to create the Linear Model and Output R-squared
	model = sm.OLS(y_sorted_days, x_sorted_pressure)
	results = model.fit()
	with open(f"results/overall-viral-pressure-result-summary.txt", "w+") as rs:
		rs.write(results.summary().as_text())
	# print(results.summary())

def daily_analysis(file_path):
	"""Run a day-by-day analysis of the performance of the viral pressure metric"""
	X = get_viral_pressure_data(get_connectedness_data(file_path), file_path)
	y = process_y(get_case_data(file_path))

	for (country, date, val) in y:
		X[date][country] = (X[date][country], val)

	daily_results = {}	
	for (date, data) in X.items():
		# _, data = daily_data
		[x_pressure, y_days] = zip(*data.values())
		model = sm.OLS(y_days, x_pressure)
		results = model.fit()
		training_mse = eval_measures.mse(y_days, results.predict(y_days))
		daily_results[date] = (training_mse, results.rsquared)
		
	[mse, rsquared] = zip(*daily_results.values())

	# dates = daily_results.keys()
	dates = [pd.to_datetime(d) for d in daily_results.keys()]

	ax = plt.gca()
	ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
	# plt.scatter(dates, mse)	
	plt.plot_date(dates, mse)	
	plt.ylabel("MSE")
	plt.xlabel("Date")
	plt.savefig("results/MSE_daily_scatter.png")
	plt.clf()

	ax = plt.gca()
	ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
	# plt.scatter(dates, rsquared)
	plt.plot_date(dates, rsquared)
	plt.ylabel("R-Squared")
	plt.xlabel("Date")
	plt.savefig("results/R_Squared_daily_scatter.png")
	plt.clf()


def train_test_split(x, y, test_pct):
	"""input:
	x: list of x values,
	y: list of independent values, 
	test_pct: percentage of the data that is testing data=0.2.

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


# TODO: different viral pressure metrics
	# 1. Try not weighting by population
	# 2. Try different ways of measuring days to infection (once infected, just n?)
# TODO: try running with only the nonzero x values

# TODO: Fill in these stencils
def get_routes(database_path):
	"""
	Takes a path to the database and produces a list of countries and the number
	of incoming flight routes
	"""
	route_query = """
	select
		a2.country as arrival_country,
		count()
	from routes
	inner join airports as a1
	on departure_code = a1.iata
	inner join airports as a2
	on arrival_code = a2.iata
	group by a2.country
	"""
	with sqlite3.connect(database_path) as conn:
		return [row for row in conn.cursor().execute(route_query)]


def get_population_data(database_path):
	"""Takes a path and produces a list of countries and their populations"""
	population_query = """select name, population, density from countries"""
	with sqlite3.connect(database_path) as conn:
		return [row for row in conn.cursor().execute(population_query)]


def overall_single_regressions(x_train, x_test, y_train, y_test):
	"""
	Run a regression over the whole timeline for each variable.
	x and y should be Pandas dataframes.
	"""
	for column in x_train.columns:
		plt.scatter(x_train[column], y_train)
		plt.ylabel("Days to infection")
		plt.xlabel(column)
		plt.savefig(f"results/single-regressions/{column}-scatter.png")
		plt.clf()

		plt.hist(x_train[column])
		plt.ylabel(column)
		plt.savefig(f"results/single-regressions/{column}-histogram.png")
		plt.clf()

		# Use StatsModels to create the Linear Model and Output R-squared
		model = sm.OLS(y_train, x_train[column])
		results = model.fit()
		# print(f"{column} regression summary:")
		with open(f"results/single-regressions/{column}-result-summary.txt", "w+") as rs:
			rs.write(results.summary().as_text())
			training_mse = eval_measures.mse(y_train, results.predict(x_train[column]))
			testing_mse = eval_measures.mse(y_test, results.predict(x_test[column]))
			rs.write("\n training MSE: " + str(training_mse))
			rs.write("\n testing MSE: " + str(testing_mse))
		# print(results.summary(), "\n\n")
	return


def overall_multiregression(x_train, x_test, y_train, y_test):
	"""
	Run a multigression over the whole timeline with all provided variables.
	x and y should be Pandas dataframes.
	"""
	# Use StatsModels to create the Linear Model and Output R-squared
	x_train = sm.add_constant(x_train)
	x_test = sm.add_constant(x_test)
	model = sm.OLS(y_train, x_train)
	results = model.fit()
	# print(f"Multiregression summary:")
	with open(f"results/multiregression-result-summary.txt", "w+") as rs:
		rs.write(results.summary().as_text())
		training_mse = eval_measures.mse(y_train, results.predict(x_train))
		testing_mse = eval_measures.mse(y_test, results.predict(x_test))
		rs.write("\n training MSE: " + str(training_mse))
		rs.write("\n testing MSE: " + str(testing_mse))
	# print(results.summary())
	return



if __name__ == "__main__":
	pp = pprint.PrettyPrinter()
	p = 0.2
	db_path = "data.db"

	routes = get_routes(db_path)
	route_countries = set([route[0] for route in routes])
	population_data = get_population_data(db_path)
	pop_countries = set([r[0] for r in population_data])

	# TODO: There are problems with which countries do or don't in different
	# tables. See the below print statements. Clean up countries that have different
	# spellings and decide what to do with countries that don't have data.
	# print("Num countries in routes table:", len(routes))
	# print("Num countries in countries table:", len(population_data))
	# print("Symmetric difference (in either but no both):")
	# pp.pprint(route_countries ^ pop_countries)
	# print("In population but not routes:")
	# pp.pprint(pop_countries - route_countries)
	# print("In routes but not populations:")
	# pp.pprint(route_countries - pop_countries)
	
	# TODO: Would like to turn it all into a single df but can't
	# do this until routes and population line up
	# x_df["routes"] = routes


	## analysis: days until first infection, predicted by population and density

	y = process_y(get_case_data(db_path))
	# Restrict y to days from days zero
	days_to_first_infection = [row for row in y if row[1] == "2020-01-22"]
	# TODO: Here, again, we've got trouble with aligning countries
	# For now, restricting y and x to their intersection is a start
	days_to_first_infection = [row for row in days_to_first_infection if row[0] in pop_countries]

	## sort, for pairing x and y (not sure 100% if this is necessary?)
	# days_to_first_infection.sort(lambda x: x[0])
	# population_data.sort(lambda x: x[0])

	# Exclude the country column
	subset_population_data = [row[1:] for row in population_data if row[0] in [d[0] for d in days_to_first_infection]]

	# clear out country and date values	
	only_days = [row[2] for row in days_to_first_infection]

	# Use train test split to split data into x_train, x_test, y_train, y_test #
	(x_train, x_test, y_train, y_test) = train_test_split(subset_population_data, only_days, p)

	# # Put data into a dataframe
	columns = ["population", "density"]
	x_test = pd.DataFrame(x_test, columns=columns)
	x_train = pd.DataFrame(x_train, columns=columns)



	# # Run overall regressions on each individual variable
	# # TODO: Write single_regressions
	overall_single_regressions(x_train, x_test, y_train, y_test)

	# # # Run a multi-regression on all variables
	# # # TODO: Write overall_multiregression
	overall_multiregression(x_train, x_test, y_train, y_test)

	# # # Run an overall regression on viral pressure
	overall_viral_pressure_analysis(db_path, y)

	# # Run a day-by-day analsysis on viral pressure
	daily_analysis(db_path)


	## Analysis: Number of cases by day&country, according to past



	exit(0)