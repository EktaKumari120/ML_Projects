import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from weather_fetcher import get_current_weather, get_forecast

st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Weather Dashboard")
st.markdown("Live weather data powered by OpenWeatherMap")

city = st.text_input("Enter a city name", value="Mumbai")

if city:
    current = get_current_weather(city)
    
    if current.get('cod') != 200:
        st.error(f"City not found. Please check the spelling and try again.")
    else:
        st.subheader(f"Current Weather in {current['name']}, {current['sys']['country']}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🌡️ Temperature", f"{current['main']['temp']}°C",
                      f"Feels like {current['main']['feels_like']}°C")
        with col2:
            st.metric("💧 Humidity", f"{current['main']['humidity']}%")
        with col3:
            st.metric("💨 Wind Speed", f"{current['wind']['speed']} m/s")
        with col4:
            st.metric("👁️ Visibility", f"{current['visibility'] // 1000} km")

        st.markdown("---")

        forecast_df = get_forecast(city)

        st.subheader("📈 5-Day Temperature Forecast")
        fig_temp  = px.line(
            forecast_df,
            x = 'datetime',
            y = 'temp',
            labels={'datetime': 'Date & Time', 'temp': 'Temperature (°C)'},
            markers=True
        )
        fig_temp.update_traces(line_color = '#e05c2a', line_width=2)
        fig_temp.update_layout(hovermode = 'x unified')
        st.plotly_chart(fig_temp,use_container_width=True)

        st.subheader("🌧️ Rain Probability (next 5 days)")
        fig_rain = px.bar(
            forecast_df,
            x = 'datetime',
            y = 'rain_prob',
            labels={'datetime': 'Date & Time', 'rain_prob': 'Rain Probability (%)'},
            color = 'rain_prob',
            color_continuous_scale= 'Blues'
        )
        fig_rain.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_rain,use_container_width=True)

        st.subheader("📋 Detailed Forecast Table")
        display_df = forecast_df.copy()
        display_df['datetime'] = display_df['datetime'].dt.strftime('%d %b, %I:%M %p')
        display_df.columns = ['Date & Time', 'Temp (°C)', 'Feels Like (°C)',
                               'Humidity (%)', 'Condition', 'Rain Prob (%)']
        display_df['Rain Prob (%)'] = display_df['Rain Prob (%)'].round(1)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
