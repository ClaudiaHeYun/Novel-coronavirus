from analysis import get_connectedness_data
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Get connectedness will give you an array with all the data necessary for viz
# Feel free to tweak get_connectedness_data if you need more data though

# Converts data into dataframe
def get_data_as_dataframe(data):
    return pd.DataFrame(data)

# Creates a new dataframe consisting only of countries with non zero viral pressure
def get_relevant_data(df):
    return df[df['4/12/20']>0]

# Plots viral pressure over time for each country
def plot_time_series_each_country(df, x, y, country):
    fig = px.line(df, x, y)
    fig.update_layout(
        title=country,
        xaxis_title="Time",
        yaxis_title="Viral Pressure",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        )
    )
    fig.show()
# Plots viral pressure over time for all countries with relevant data
def plot_time_series_all_countries(df, x_values, y_values, countries):
    fig = go.Figure()
    n = len(countries)

    for i in range(n):
        fig.add_trace(go.Scatter(
            x = x_values,
            y = y_values[i],
            name = countries[i]
        ))

    fig.update_layout(
        title="Viral Pressures by Country",
        xaxis_title="Time",
        yaxis_title="Viral Pressure",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        )
    )
    fig.show()

if __name__ == "__main__":
    # Reads in data from analysis.py
    data = get_connectedness_data("../data.db")
    # Converts data from dictionary to dataframe
    df = get_data_as_dataframe(data) 
    # Removes columns with only 0s 
    df = get_relevant_data(df)
    # print(df)
    # print(df.describe())
        
    # Stores relevant countries in an array
    countries = df.index.values
    # Stores time as x_data array
    x_data = df.columns.values  
    # y is stored as numpy array of arrays
    y_data = df.to_numpy()

    # PLots viral pressure time series graph for each country individually
    # for i in range(5):
    #     plot_time_series_each_country(df, x_data, y_data[i], countries[i])

    # Plots viral pressure time series graph for every country side by side
    plot_time_series_all_countries(df, x_data, y_data, countries)    

    