# Data Deliverable

## Goal

Use flight route traffic to establish a measure of connectedness between cities interationally. With this connectedness measure and case numbers, predict the spread in case/10,000 of CoVID-19 globally. In certain regions where intranational data is available, we plan to predict spread between states/provinces/territories.

## Data Spec

Data for this project was pulled from a number of different sources so rather than describe the source CSV’s this data specification describes the data created from all of the different sources. Within the `data` folder there are three subfolders, `flights`, `population`, and `virus`. The flights folder uses data pulled from OpenFlights, the population folder has csv files pulled from the US, Canadian, Australian, and Chinese census bureaus’ websites and is pulled from the latest available year which was 2018, with the exception of Canada for which the latest available year was 2016.

Our data is loaded into a SQLite database called data.db via a Python script (db_create.py) and contains the following tables:

- `countries`:
  - `name` :: Text - The name of the country and the primary key for the table.
  - `year` :: INTEGER - The year in which population data was gathered.
  - `population` :: INTEGER NOT NULL - The number of people estimated to be living in the country.
  - `area` :: REAL NOT NULL - The area of the country in square kilometers.
  - `density` :: REAL NOT NULL - Population density per square kilometer.

- `states`: 
  - `name` :: TEXT NOT NULL - The name of the state, province, or territory. This is the primary key.
  - `abbreviation`  :: TEXT - Abbreviation if one exists, since some of the case data for US locations use postal abbreviations for US states.
  - `country` :: TEXT NOT NULL - This is a foreign key to the countries tables.
  - `population` :: INTEGER - The population of the state.

- `cities`:
  - `name` :: TEXT NOT NULL - The name of the city and the primary key.
  - `state` :: TEXT NOT NULL - The name of the state and a foreign key to the name column in the states table.
  - `population` :: INTEGER - The population of the state.

- `cases`:
  - `id` :: INTEGER - An auto-incremented id which is the primary key for this table.
  - `state` :: TEXT - The state, province, or territory in which the associated cases originated. This level of detail is only available from the US, Canada, Australia, and China at the time we pulled data.
  - `country` :: TEXT - The country in which the case originated.
  - `confirmed` :: INTEGER - A count of the number of confirmed cases in the region.
  - `deaths` :: INTEGER - A count of the number of deaths in the region.
  - `recovered` :: INTEGER - A count of the number of recovered cases in the region.
- `airports`:
  - `airport_id` :: INTEGER - Primary key for the table.
  - `name` :: TEXT - The airport name. May not be unique.
  - `city` :: TEXT NOT NULL - The city in which the airport is located.
  - `country` :: TEXT NOT NULL - The country in which the airport is located.
  - `iata` :: TEXT NOT NULL - A three letter code issued by the International Air Transport Association, which is a trade association. These are the codes that usually appear on tickets and other customer-facing documents.
  - `icao` :: TEXT NOT NULL - A code issued by the International Civil Aviation Organization, which is used for official planning such as air traffic control and flight planning.
- `routes`:
  - `id` :: INTEGER - An auto-incremented primary key.
  - `departure_code` :: TEXT - A code designating the departure airport which can be either IATA or ICAO.
  - `arrival_code` :: TEXT - A code designating the arrival airport which can be either IATA or ICAO.

The sources for the various CSV from which we pulled data can be found below:

- `/flights/*`: https://openflights.org/data.html
- `/virus/cleanedInfections.csv`: https://github.com/CSSEGISandData/COVID-19
- `/populations/`:
  - `australia-populations-2018.csv` - Table 4 from https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/3101.0Jun%202019?OpenDocument
  - `canada-provinces-2016.csv` - https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000901
  - `china-populations-2018.csv` - Indications > Population > Total Population http://data.stats.gov.cn/english/easyquery.htm?cn=E0103
  - `country-populations-2018.csv` -  https://www.census.gov/data-tools/demo/idb/informationGateway.php
  - `us-cities-populations-2018.csv` - https://www.census.gov/data/tables/time-series/demo/popest/2010s-total-cities-and-towns.html#ds
  - `us-states-populations-2018.csv` - https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html#par_textimage_1873399417


## How to download

All the data for this project can be found in [this repo](https://github.com/ClaudiaHeYun/Novel-coronavirus) in `/data` which contains `population/`, `flights/`, and `virus`.
Population has data about places and their populations, flights has information about airports and routes between them, and
virus has case report data.

## Sample Data

A sample of your data (e.g. 10 - 100 rows) that we can easily open and view on our computers.

Flights:
```
1|Alabama|Alabama|4887871
2|Abbeville city|Alabama|2563
3|Adamsville city|Alabama|4325
4|Addison town|Alabama|724
5|Akron town|Alabama|330
6|Alabaster city|Alabama|33340
7|Albertville city|Alabama|21568
8|Alexander City city|Alabama|14467
9|Aliceville city|Alabama|2301
10|Allgood town|Alabama|622
```

States:
```
United States|AK|United States of America|326687501
Northeast Region|AL|United States of America|56046620
Midwest Region|AR|United States of America|68236628
South Region|AZ|United States of America|124569433
West Region|CA|United States of America|77834820
Alabama|CO|United States of America|4887681
Alaska|CT|United States of America|735139
Arizona|DE|United States of America|7158024
Arkansas|DC|United States of America|3009733
California|FL|United States of America|39461588
```

Countries:
```
Afghanistan|2020|36643815|652230.0|56.2
Albania|2020|3074579|27398.0|112.2
Algeria|2020|42972878|2381740.0|18.0
American Samoa|2020|49437|198.0|250.0
Andorra|2020|85635|468.0|183.0
Angola|2020|32522339|1246700.0|26.1
Anguilla|2020|18090|91.0|198.8
Antigua and Barbuda|2020|98179|443.0|221.8
Argentina|2020|45479118|2736690.0|16.6
Armenia|2020|3021324|28203.0|107.1
```

Cases:
```
1|Hubei|Mainland China|67666|2959|43500
2||South Korea|7041|44|135
3||Italy|5883|233|589
4||Iran|5823|145|1669
5|Guangdong|Mainland China|1352|7|1237
6|Henan|Mainland China|1272|22|1244
7|Zhejiang|Mainland China|1215|1|1154
8|Hunan|Mainland China|1018|4|960
9|Anhui|Mainland China|990|6|979
10||France|949|11|12
```

Airports:
```
1|Goroka Airport|Goroka|Papua New Guinea|GKA|AYGA
2|Madang Airport|Madang|Papua New Guinea|MAG|AYMD
3|Mount Hagen Kagamuga Airport|Mount Hagen|Papua New Guinea|HGU|AYMH
4|Nadzab Airport|Nadzab|Papua New Guinea|LAE|AYNZ
5|Port Moresby Jacksons International Airport|Port Moresby|Papua New Guinea|POM|AYPY
6|Wewak International Airport|Wewak|Papua New Guinea|WWK|AYWK
7|Narsarsuaq Airport|Narssarssuaq|Greenland|UAK|BGBW
8|Godthaab / Nuuk Airport|Godthaab|Greenland|GOH|BGGH
9|Kangerlussuaq Airport|Sondrestrom|Greenland|SFJ|BGSF
10|Thule Air Base|Thule|Greenland|THU|BGTL
```

Routes:
```
1|AER|KZN
2|ASF|KZN
3|ASF|MRV
4|CEK|KZN
5|CEK|OVB
6|DME|KZN
7|DME|NBC
8|DME|TGK
9|DME|UUA
10|EGO|KGD
```

## Tech Report

### Data Collection

#### Cases

This data is from Johns Hopkins University, and they have an openly-available github repository of cases that gets updated every day. They synthesize their data from a variety of reports, which might account for some minor inconsistencies that we saw. On the whole, however, it’s pretty reputable; their visualization and data are basically the ones being used by everyone else on the internet by some degree of separation or another. This data is definitely somewhat inaccurate, however, in that it’s only confirmed cases, and mild cases or cases where testing kits are unavailable (which has been true in the US) are underreported.


#### Flights

This flight data is from openflights.org. The two data files were in the form of .dat files. We were then able to convert these files into .csv by changing the file extension. Openflights appears to be a reputable source. It contains dedicated Twitter and Facebook pages with over 600 followers and is often referenced on the datasets subreddit. The one thing of note is that the routes file was last updated 3 years ago since the upstream source disappeared and the airports file was last updated 10 months ago. So, the data we collected is not the most up to date.


#### Population

This data was pulled from the Canadian, Australian, US, and Chinese census bureaus. Since this is a crucial government metric, we can be reasonably confident about the veracity and cleanliness of the data, although you never know.

### Data Cleanliness

#### Cases

The virus data needed some cleaning - information about cases in the US were by county in each state, whereas we wanted the data by state or province for US, China, Australia, and Canada. For cleaning, we collapsed all the different county entries into the same state. As this is also *all* of the known cases of Covid-19 (as of a few days ago, and relatively easily updatable), we definitely have all the data we need. In total, this is around 100,000 cases, aggregated by location, for ~170 locations. We’ve fixed and cleaned data type issues, for the most part.

We did remove some data, however. Some cases, such as those on the diamond princess cruise ship, weren’t relevant to our model - focusing on connectedness between countries - and the people involved are unlikely to spread the disease, given that they are already quarantined and monitored. Moreover, we don’t know where many of these people will be sent, so we predict that these numbers will become integrated into the totals if we re-run our cleaning on updated data.

One of the difficulties that we’ve seen just in the past few days is just how fast the disease spreads - or perhaps how many cases went unaccounted for, even recently. For example, Massachusetts went from 7 cases to 92 in the span of the last few days. Making sure our data is accurate is going to be especially difficult when real health agencies are struggling to keep up. One thing to note: it seems that JHU changed their database format in the last few days, removing the need for our cleaning work in this area, but we did actually have an R script to do it. We will probably create an updated script to do the new cleaning necessary.

#### Flights

The data did not require cleaning. The routes file contained 67663 rows and 9 columns of data. The airports file contained 7698 rows and 14 columns of data. The CODESHARE column in routes was empty but that wasn’t data we required.

We did remove data when we converted the csv into a database. From routes, we only kept id, DEP_ID (departure code), and ARR_ID (arrival code). From airports, we only kept AIRPORT_ID, NAME, CITY, COUNTRY, IATA, and ICAO. The data we removed included LATITUDE, LONGITUDE, and TIMEZONE. None of this was required for the purposes of our project.


#### Population

Luckily since this data is one of the top-line number for census bureaus worldwide, this data was quite clean and we haven't yet uncovered any issues.

How clean is the data? Does this data contain what you need in order to complete the project you proposed to do? (Each team will have to go about answering this question differently, but use the following questions as a guide. Graphs and tables are highly encouraged if they allow you to answer these questions more succinctly.)


### Next Steps

We are going to use the airport codes to determine the connectedness between different countries/states.
