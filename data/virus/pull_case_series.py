import requests
import csv
import json

def add_rows(a, b):

	return []

def parse_row(row):
	return []

if __name__ == "__main__":
	# Get CSV
	SERIES_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
	r = requests.get(SERIES_URL)
	# Collapse states into single country
	countries = {}
	for row in csv.DictReader(r.content):
		cur_country = row["Country/Region"]
		if cur_country in countries:
			old_row = countries[cur_country]
			cur_row = parse_row(row)
			new_row = add_rows(old_row, cur_row)
		else:
			cur_row = parse_row(row)
			countries[cur_row] = row.keys
	# Write out the simplified json
	with open("case_series.json", "w") as case_file:
		json.dump(countries, case_file)


