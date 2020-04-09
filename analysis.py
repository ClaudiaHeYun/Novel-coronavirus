import sqlite3
import numpy as np
import pandas as pd
import random
import csv
from scipy import stats
import statsmodels.api as sm
from statsmodels.tools import eval_measures
import statsmodels.formula.api as smf

conn = sqlite3.connect('data.db')
c = conn.cursor()

connectedness_query = """
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
);
"""
"""
route_data = {
	departure_code :: String,
	arrival_code :: String 
	passenger_volume :: Integer,
	departure_country :: String,
	arrival_country :: String,
}
"""
route_data = c.execute(connectedness_query)

case_query = """
select date, country, cases
from cases
where country is not null
"""
"""
case_data = {
	date :: Date,
	country :: String,
	cases :: Integer,
	population :: Integer
}
"""
case_data = c.execute(case_query)

# Join case data and route data on country
# We now have a time series of cases of over time matched with
# flight route data. This is our baseline dataset.
# Probably create a pandas dataframe here
joined_data = []

# Compute case rates by dividing case counts by population
# We may want to experiment during the regression step with
# different ways of generating this number.
# Now we have something we can do regression on
X = joined_data

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
	# TODO: use train test split to split data into x_train, x_test, y_train, y_test #
	(x_train, x_test, y_train, y_test) = train_test_split(X, y, p)
	# print(type(x_train), type(x_test), type(y_train))

	# TODO: Use StatsModels to create the Linear Model and Output R-squared
	x_train = sm.add_constant(x_train) # add a constant column to be intercept
	model = sm.OLS(y_train, x_train)
	results = model.fit()
	print(results.summary())

	# Prints out the Report
	# TODO: print R-squared, test MSE & train MSE
	print(f"R2: {results.rsquared}")
	training_mse = eval_measures.mse(y_train, results.predict(x_train))
	print(f"Training MSE: {training_mse}")
	x_test = sm.add_constant(x_test)
	predicted_y_test = results.predict(x_test)
	testing_mse = eval_measures.mse(y_test, predicted_y_test)
	print(f"Testing MSE: {testing_mse}")
	exit(0)
