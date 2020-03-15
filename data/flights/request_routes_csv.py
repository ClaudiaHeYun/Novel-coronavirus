import requests
import csv

HOST = "https://api.flightstats.com/flex/schedules/rest"
appId = "f095c287"
# DO NOT PUSH THIS KEY
appKey = ""

# For each route in the routes CSV request flight data on our chosen analysis date=
with open("./top-100-routes.csv") as routes_csv, open("./route_traffic.csv", "w") as traffic_csv:
	routes_reader = csv.DictReader(routes_csv)
	traffic_writer = csv.writer(traffic_csv)
	traffic_writer.writerow(["departure code", "arrival code", "scheduled flights", "number of flights"])

	limit = 1
	cnt = 0
	for route in routes_reader:
		# REQUESTS COST MONEY!
		route_string = route["Route by code"]
		(departure_code, arrivale_code) = route_string.split("-")
		departure_code = "KSFO" #route["DEP"]
		arrival_code = "KJFK" # route["ARR"]
		(year, month, day) = ("2020", "3", "12")
		res = requests.get(f"{HOST}/v1/json/from/{departure_code}/to/{arrival_code}/departing/{year}/{month}/{day}",
			params={"appId": appId, "appKey": appKey})
		json = res.json()
		if res.status_code != 200 or json["error"]["httpStatusCode"] != 200:
			print(f"Request failed: {res.url}")
		else:
			traffic_writer.writerow([departure_code, arrival_code, json.scheduled_flights, len(json.scheduled_flights)])
		cnt += 1
		if cnt == limit:
			break