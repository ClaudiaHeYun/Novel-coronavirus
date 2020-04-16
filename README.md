# Predicting the spread of SARS-CoV-2 globally based on international flight traffic

Final project for CS1951A Data Science @ Brown University

## Goal

Use traffic on international flight routes along with early Coronavirus case data to predict which countries with no cases yet are most likely to see their first infections.

## Usage

Use `pipenv install` to install the necessary packages for running our scripts, then use `pipenv shell` and `python <script.py>`, or `pipenv run <script.py>` to run our scripts.

## Project Layout

- `data.db` is the data with all of our data. It can be rebuilt from the contents of `/data` with db_create.py
- `/data` contains `/virus`, `/flights`, and`/population` which each contain our data files and the scripts we used to pull in the data. `/virus` has daily data case data for each country. `/population` has population numbers for geographic region such as countries and states. `/flights` has data about each airport, data about each active flight route, and traffic volume for the top 100 flight routes in 2018.
- `/data-deliverable` has the markdown and html for our data deliverable report. This information is now outdated.
- `/stats-viz-deliverable` has some preliminary results and analysis along with markdown and html files writing up these initial results.

## Contributors

Quinn Abrams, Evan Dong, Varun Senthil Nathan, and Claudia He Yun 
