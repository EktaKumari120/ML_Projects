import requests
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/"


@st.cache_data(ttl=600)
def get_current_weather(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data


@st.cache_data(ttl=600)
def get_forecast(city):
    url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    forecast_list = []

    for item in data['list']:
        forecast_list.append({
            'datetime': datetime.fromtimestamp(item['dt']),
            'temp': item['main']['temp'],
            'feels_like': item['main']['feels_like'],
            'humidity': item['main']['humidity'],
            'description': item['weather'][0]['description'],
            'rain_prob': item.get('pop', 0) * 100
        })

    df = pd.DataFrame(forecast_list)
    return df


if __name__ == "__main__":
    print("--- Current Weather ---")
    current = get_current_weather("Mumbai")
    print("Temperature:", current['main']['temp'])
    print("Feels like:", current['main']['feels_like'])
    print("Condition:", current['weather'][0]['description'])

    print("\n--- Forecast (first 5 rows) ---")
    forecast_df = get_forecast("Mumbai")
    print(forecast_df.head())
