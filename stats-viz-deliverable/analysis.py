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
from sklearn.model_selection import train_test_split


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
	dates = [pd.to_datetime(d, format="%Y-%m-%d") for d in daily_results.keys()]

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


# TODO: Fill in these stencils
def get_routes(database_path):
	"""
	Takes a path to the database and produces a list of countries and the number
	of incoming international flight routes
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
	where a1.country != a2.country
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
		x = x_train[column]
		plt.scatter(x, y_train)
		plt.ylabel("Days to first infection")
		plt.xlabel(column.replace("-", " ").title())
		plt.savefig(f"results/single-regressions/{column}-scatter.png")
		plt.clf()

		plt.hist(x_train[column])
		plt.ylabel(column.replace("-", " ").title())
		plt.savefig(f"results/single-regressions/{column}-histogram.png")
		plt.clf()

		# Use StatsModels to create the Linear Model and Output R-squared
		model = sm.OLS(y_train, x_train[column])
		results = model.fit()
		# print(f"{column} regression summary:")
		with open(f"results/single-regressions/{column}-result-summary.txt", "w+") as rs:
			rs.write(results.summary().as_text())
			training_mse = eval_measures.mse(y_train, pd.DataFrame(results.predict(x_train[column])))
			testing_mse = eval_measures.mse(y_test, pd.DataFrame(results.predict(x_test[column])))
			rs.write("\n training MSE: " + str(training_mse[0]))
			rs.write("\n testing MSE: " + str(testing_mse[0]))
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
		# TODO: Something is messed up here
		training_mse = eval_measures.mse(y_train, pd.DataFrame(results.predict(x_train)))
		testing_mse = eval_measures.mse(y_test, pd.DataFrame(results.predict(x_test)))
		rs.write("\n training MSE: " + str(training_mse[0]))
		rs.write("\n testing MSE: " + str(testing_mse[0]))
	# print(results.summary())
	return


if __name__ == "__main__":
	pp = pprint.PrettyPrinter()
	db_path = "../data.db"

	# Get routes and a set of all countries in route data
	# Intersecting all these sets will allow us to cull rows from our data before
	# running our multiregression
	routes = get_routes(db_path)
	route_countries = set([route[0] for route in routes])

	population_data = get_population_data(db_path)
	pop_countries = set([r[0] for r in population_data])

	# Y is a time series for all countries for all days
	y_time_series = process_y(get_case_data(db_path))
	# Restrict y to days from days zero
	# TODO: Here, again, we've got trouble with aligning countries unless we do better clean when making db
	days_to_first_infection = [row for row in y_time_series if row[1] == "2020-01-22"]
	# A set of countries for which we have case data
	case_countries = set([row[0] for row in days_to_first_infection])

	# # TODO: There are problems with which countries do or don't appear in different
	# # tables. See the below print statements. Clean up countries that have different
	# # spellings and decide what to do with countries that don't have data.
	# print("Num countries in routes table:", len(routes))
	# print("Num countries in countries table:", len(population_data))
	# print("Num countries in cases table:", len(case_countries))
	# print("Symmetric difference (in either but not both):")
	# pp.pprint((route_countries | pop_countries) ^ case_countries)

	# Take the intersection of the countries present in all countries
	# then only include these countries in the multi-regression
	# 169 countries make it into this intersections, which should be enough
	intersect_countries_of_all_vars = route_countries & pop_countries & case_countries

	# Restrict y to only rows where the country appears in the intersection
	days_to_first_infection = [row[2] for row in days_to_first_infection if row[0] in intersect_countries_of_all_vars]

	# # Sanity check alignment of rows. Uncomment and run when making changes.
	# check_pop_data = [row for row in population_data if row[0] in intersect_countries_of_all_vars]
	# check_route_data = [row for row in routes if row[0] in intersect_countries_of_all_vars]
	# # Checks that all rows line up
	# print("Do all rows line up?", all([prow[0] == rrow[0] and prow[0] == drow[0] for prow, rrow, drow in zip(check_pop_data, check_route_data, days_to_first_infection)]))

	# # Exclude the country column and take only data that has a country that's in the intersection of all variables
	# Reminder that population data has both population and density in it
	subset_population_data = [row[1:] for row in population_data if row[0] in intersect_countries_of_all_vars]
	# Split up population data
	pop_data = [row[0] for row in subset_population_data]
	density_data = [row[1] for row in subset_population_data]
	subset_route_data = [route[1] for route in routes if route[0] in intersect_countries_of_all_vars]
	# You can add countries to either x or y to make it easy to see which rows correspond to which country if you need
	countries = [row[0] for row in population_data]

	columns = ["population", "density", "number-of-incoming-routes"]
	X = pd.DataFrame(zip(pop_data, density_data, subset_route_data), columns=columns)
	y_columns = ["days_to_first_infection"]
	y = pd.DataFrame(zip(days_to_first_infection), columns=y_columns)

	# Split data into x_train, x_test, y_train, y_test
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)

	# Run overall regressions on each individual variable
	overall_single_regressions(X_train, X_test, y_train, y_test)

	# Run a multi-regression on all variables
	overall_multiregression(X_train, X_test, y_train, y_test)

	# # Run an overall regression on viral pressure
	overall_viral_pressure_analysis(db_path, y_time_series)

	# Run a day-by-day analsysis on viral pressure
	# daily_analysis(db_path)

	# TODO: Stretch analysis would be countin the number of "hot" routes on a daily basis based
	# on whether those routes are coming from infected countries

	exit(0)