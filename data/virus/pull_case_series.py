import requests
import csv
import json
import io

def add_rows(a, b):
	"""Add up case totals between two rows"""
	country = a[0]
	return (country, [i + j for i, j in zip(a[1], b[1])])

def parse_row(row):
	"""Takes a row and converts each field to the appropriate type"""
	_, country, lat, lon, *daily_totals = row
	lat = float(lat)
	lon = float(lon)
	if country == "US":
		country = "United States"
	if country == "Taiwan*":
		country = "Taiwan"
	daily_totals = [int(total) for total in daily_totals]
	return (country, daily_totals)

if __name__ == "__main__":
	# Get CSV
	SERIES_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
	r = requests.get(SERIES_URL)
	# Collapse states into single country
	countries = {}
	f = io.StringIO(r.text)
	reader = csv.reader(f)
	# NOTE: The header row will be useful when running time series
	labels = next(reader) # skip header line
	dates = []
	for date in labels[4:]:
		month, day, year = date.split("/")
		month = "0" + month if len(month) == 1 else month
		day = "0" + day if len(day) == 1 else day
		year = "20" + year
		date = "-".join([year, month, day])
		dates += [date]
	labels = ["Country", dates]
	output = { "labels": labels }
	for row in reader:
		cur_row = parse_row(row)
		cur_country = cur_row[0] # country/region
		if cur_country in countries:
			old_row = countries[cur_country]
			new_row = add_rows(old_row, cur_row)
			countries[cur_country] = new_row
		else:
			countries[cur_country] = cur_row
	output["countries"] = countries
	# Write out the simplified json
	with open("case_series.json", "w") as case_file:
		json.dump(output, case_file)


