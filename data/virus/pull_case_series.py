import requests
import csv
import json
import io

def add_rows(a, b):
	return (a[0], a[2], [i + j for i, j in zip(a[2], b[2])])

def parse_row(row):
	state, country, lat, lon, *daily_totals = row
	lat = float(lat)
	lon = float(lon)
	daily_totals = [int(total) for total in daily_totals]
	return (state, country, daily_totals)

if __name__ == "__main__":
	# Get CSV
	SERIES_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
	r = requests.get(SERIES_URL)
	# Collapse states into single country
	countries = {}
	# Using a dictreader turns the first row into fieldnames
	f = io.StringIO(r.text)
	reader = csv.reader(f)
	# NOTE: The header row will be useful when running time series
	next(reader) # skip header line
	for row in reader:
		cur_country = row[1] # country/region
		cur_row = parse_row(row)
		if cur_country in countries:
			old_row = countries[cur_country]
			new_row = add_rows(old_row, cur_row)
		else:
			countries[cur_country] = cur_row
	# Write out the simplified json
	with open("case_series.json", "w") as case_file:
		json.dump(countries, case_file)


