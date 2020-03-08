from bs4 import BeautifulSoup as BS
import requests
import sqlite3

### IEX TRADING API METHODS ###
IEX_TRADING_URL = "https://cloud.iexapis.com/stable/stock/"
base_url = "https://cloud.iexapis.com/"


### YAHOO FINANCE SCRAPING
MOST_ACTIVE_STOCKS_URL = "https://cs.brown.edu/courses/csci1951-a/resources/stocks_scraping_2020.html"

### Register at IEX to receive your unique token
TOKEN = 'pk_61d134213f2c4bb988af57dbe09b9871'

# TODO: Use BeautifulSoup and requests to collect data required for the assignment.
active_res = requests.get(MOST_ACTIVE_STOCKS_URL)
active_soup = BS(active_res.text, 'html.parser')
table = active_soup.find('table').find_all('tr')

companies = {}
quotes = {}
for row in table[1:]:
    tds = row.find_all('td')
    (_, name, symbol, price, change, change_pct, volume, hq) = tds
    # Cleaning and type conversion
    name = name.find('a').string
    symbol = symbol.string.lower().strip()
    price = float(price.string.replace(",", ""))
    change = float(change.string.replace("+", ""))
    change_pct = float(change_pct.string[:-1].replace("+", ""))
    volume = float(volume.string[:-1])
    hq = hq.string.lower().strip()
    # company :: [ skip, name :: String, ticker_symbol :: String, price :: Decimal, change_percentage :: Decimal, volume :: Decimal, HQ :: String] 
    companies[symbol] = [name, hq]
    quotes[symbol] = [price, None, None, volume, change_pct]

# "genTbl closedTbl elpTbl elp25 crossRatesTbl"

#TODO: Use IEX trading API to collect sector and news data.
for symbol in companies:
    # Request the most recent 5 day period because this is what is required
    iex_res = requests.get(f"{IEX_TRADING_URL}{symbol}/chart/5d",
                            params={"chartCloseOnly": True, "token": TOKEN})
    # Request the number of recent articles about a company
    news_res = requests.get(f"{IEX_TRADING_URL}{symbol}/news/last/10",
                            params={"token": TOKEN})
    if iex_res.status_code != 200 or news_res.status_code != 200:
        print(f"{iex_res.status_code} error from stock endpoint for {symbol}")
        print(f"{news_res.status_code} error from news endpoint for {symbol}")
        del companies[symbol]
        del quotes[symbol]
    else:
        iex_json = iex_res.json()
        prices = []
        for day in iex_json:
            prices.append(day['close'])
        avg_price = sum(prices) / len(prices)
        quotes[symbol][1] = avg_price

        DATE_CUTOFF = 1580515200000
        count = 0
        for article in news_res.json():
            if article['datetime'] >= DATE_CUTOFF:
                count += 1
        quotes[symbol][2] = count


# Create connection to database
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Delete tables if they exist
c.execute('DROP TABLE IF EXISTS "companies";')
c.execute('DROP TABLE IF EXISTS "quotes";')

#TODO: Create tables in the database and add data to it. REMEMBER TO COMMIT
symbol_type = "char(15)"
c.execute('''CREATE TABLE companies (
    symbol text NOT NULL, 
    name text, 
    location text,
    PRIMARY KEY (symbol)
)''')

c.execute('''CREATE TABLE quotes (
    symbol text NOT NULL,
    price float,
    avg_price float,
    num_articles int,
    volume float,
    change_pct float,
    PRIMARY KEY (symbol)
)''')

conn.commit()

for symbol, company in companies.items():
    (name, location) = company
    c.execute("INSERT INTO companies VALUES (?, ?, ?)", (symbol, name, location))

for symbol, quote in quotes.items():
    (price, avg_price, num_articles, volume, change_pct) = quote
    c.execute("INSERT INTO quotes VALUES (?, ?, ?, ?, ?, ?)", (symbol, price, avg_price, num_articles, volume, change_pct))

conn.commit()
conn.close()
