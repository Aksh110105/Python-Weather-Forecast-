import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for rendering plots

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from flask import Flask, jsonify, request
from io import BytesIO
import base64
from flask_cors import CORS
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load and clean the data
DATA_PATH = 'weather_data___10.csv'  # Ensure this is the correct path to your file
try:
    weather_data = pd.read_csv(DATA_PATH)
    logging.info("Weather data loaded successfully.")
except FileNotFoundError:
    weather_data = pd.DataFrame(columns=['city', 'date', 'max_temp', 'min_temp', 'avg_temp', 'humidity', 'precipitation'])
    logging.error("Weather data file not found.")

# Data Cleaning Function
def clean_data(data):
    data['date'] = pd.to_datetime(data['date'], errors='coerce')
    data.dropna(subset=['date', 'precipitation', 'humidity', 'avg_temp'], inplace=True)
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['city'] = data['city'].str.strip()
    return data

weather_data = clean_data(weather_data)

# Machine Learning Models
scaler = StandardScaler()

def train_models(city_data):
    X = city_data[['year', 'month']]
    y_precipitation = city_data['precipitation']
    y_humidity = city_data['humidity']
    y_temperature = city_data['avg_temp']

    # Scaling the data
    X_scaled = scaler.fit_transform(X)

    # Train Linear Regression models
    model_precipitation = LinearRegression().fit(X_scaled, y_precipitation)
    model_humidity = LinearRegression().fit(X_scaled, y_humidity)
    model_temperature = LinearRegression().fit(X_scaled, y_temperature)

    return model_precipitation, model_humidity, model_temperature

# Function to convert image to base64
def img_to_base64(img_buf):
    img_buf.seek(0)
    return base64.b64encode(img_buf.read()).decode('utf-8')

# Routes
@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required.'}), 400

    # Filter city data
    city_data = weather_data[weather_data['city'].str.title() == city.title()]
    if city_data.empty:
        return jsonify({'error': f'No data available for {city}.'}), 404

    # Fetch the latest data
    latest_entry = city_data.iloc[-1].to_dict()

    # Log the data for debugging
    logging.info(f"Latest data for {city}: {latest_entry}")

    # Return weather data
    return jsonify({
        'city': latest_entry.get('city', 'N/A'),
        'avg_temp': latest_entry.get('avg_temp', 'N/A'),
        'precipitation': latest_entry.get('precipitation', 'N/A'),
        'humidity': latest_entry.get('humidity', 'N/A'),
    })


@app.route('/forecast', methods=['GET'])
def forecast():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required.'}), 400

    city_data = weather_data[weather_data['city'].str.title() == city.title()]
    if city_data.empty:
        return jsonify({'error': f'No data available for {city}.'}), 404

    try:
        model_precipitation, model_humidity, model_temperature = train_models(city_data)

        # Predict for future years 2025–2032
        future_years = pd.DataFrame({'year': np.repeat(range(2025, 2033), 12), 'month': list(range(1, 13)) * 8})
        future_scaled = scaler.transform(future_years)
        future_precipitation = model_precipitation.predict(future_scaled)
        future_humidity = model_humidity.predict(future_scaled)
        future_temperature = model_temperature.predict(future_scaled)

        future_years['precipitation'] = future_precipitation
        future_years['humidity'] = future_humidity
        future_years['temperature'] = future_temperature

        # Plot Hot Weather (threshold = 29°C)
        hot_weather = city_data[city_data['avg_temp'] > 29]
        plt.figure(figsize=(12, 6))
        if not hot_weather.empty:
            for city in hot_weather['city'].unique():
                city_hot = hot_weather[hot_weather['city'] == city].groupby('year')['avg_temp'].count()
                plt.plot(city_hot.index, city_hot.values, marker='o', label=f"Hot Weather in {city}")
            plt.legend()
        plt.title('Hot Weather Trends (2014–2024)')
        plt.xlabel('Year')
        plt.ylabel('Number of Hot Weather Days')
        hot_weather_buf = BytesIO()
        plt.savefig(hot_weather_buf, format='png')
        hot_weather_base64 = img_to_base64(hot_weather_buf)
        plt.close()

        # Plot Cold Weather (threshold = < 19°C)
        cold_weather = city_data[city_data['avg_temp'] < 19]
        print(f"Cold weather data count: {len(cold_weather)}")
        plt.figure(figsize=(12, 6))
        if not cold_weather.empty:
            for city in cold_weather['city'].unique():
                city_cold = cold_weather[cold_weather['city'] == city].groupby('year')['avg_temp'].count()
                plt.plot(city_cold.index, city_cold.values, marker='o', label=f"Cold Weather in {city}")
            plt.legend()
        plt.title('Cold Weather Trends (2014–2024)')
        plt.xlabel('Year')
        plt.ylabel('Number of Cold Weather Days')
        cold_weather_buf = BytesIO()
        plt.savefig(cold_weather_buf, format='png')
        cold_weather_base64 = img_to_base64(cold_weather_buf)
        plt.close()

        # Plot Future Precipitation for each year from 2025–2032
        plt.figure(figsize=(12, 6))
        for i in range(2025, 2033):
            months_for_year = future_years[future_years['year'] == i]['month']
            precip_for_year = future_precipitation[(i - 2025) * 12 : (i - 2025 + 1) * 12]
            plt.plot(months_for_year, precip_for_year, label=f'Precipitation {i}')
        plt.title(f"Future Precipitation Predictions for {city} (2025–2032)")
        plt.xlabel('Month')
        plt.ylabel('Precipitation (mm)')
        plt.legend()
        future_precipitation_buf = BytesIO()
        plt.savefig(future_precipitation_buf, format='png')
        future_precipitation_base64 = img_to_base64(future_precipitation_buf)
        plt.close()

        # Plot Future Humidity for each year from 2025–2032
        plt.figure(figsize=(12, 6))
        for i in range(2025, 2033):
            months_for_year = future_years[future_years['year'] == i]['month']
            humidity_for_year = future_humidity[(i - 2025) * 12 : (i - 2025 + 1) * 12]
            plt.plot(months_for_year, humidity_for_year, label=f'Humidity {i}')
        plt.title(f"Future Humidity Predictions for {city} (2025–2032)")
        plt.xlabel('Month')
        plt.ylabel('Humidity (%)')
        plt.legend()
        future_humidity_buf = BytesIO()
        plt.savefig(future_humidity_buf, format='png')
        future_humidity_base64 = img_to_base64(future_humidity_buf)
        plt.close()

        # Plot Future Temperature for each year from 2025–2032
        plt.figure(figsize=(12, 6))
        for i in range(2025, 2033):
            months_for_year = future_years[future_years['year'] == i]['month']
            temperature_for_year = future_temperature[(i - 2025) * 12 : (i - 2025 + 1) * 12]
            plt.plot(months_for_year, temperature_for_year, label=f'Temperature {i}')
        plt.title(f"Future Temperature Predictions for {city} (2025–2032)")
        plt.xlabel('Month')
        plt.ylabel('Temperature (°C)')
        plt.legend()
        future_temperature_buf = BytesIO()
        plt.savefig(future_temperature_buf, format='png')
        future_temperature_base64 = img_to_base64(future_temperature_buf)
        plt.close()

        # Return all 5 graphs as base64-encoded images
        return jsonify({
            'hot_weather_graph': hot_weather_base64,
            'cold_weather_graph': cold_weather_base64,
            'future_precipitation_graph': future_precipitation_base64,
            'future_humidity_graph': future_humidity_base64,
            'future_temperature_graph': future_temperature_base64
        })

    except Exception as e:
        logging.error(f"Error generating forecast: {e}")
        return jsonify({'error': f"Forecast failed: {e}"}), 500


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
