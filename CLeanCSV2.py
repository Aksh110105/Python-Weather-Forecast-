import pandas as pd
import numpy as np
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

# Example: Loading the weather data CSV file
file_path = 'weather_data___10.csv'  # Adjust the file path if necessary

# Check if the file exists
if not os.path.exists(file_path):
    logging.error(f"The file {file_path} was not found.")
    exit()  # Exit if the file is not found

# Load the weather data
try:
    weather_data = pd.read_csv(file_path)
    logging.info(f"Weather data loaded successfully from {file_path}.")
except Exception as e:
    logging.error(f"Error loading the file: {e}")
    exit()

# Inspect the first few rows to understand the structure of the data
logging.info("Initial rows of the dataset:")
logging.info(weather_data.head())

# Remove duplicate rows based on all columns
weather_data.drop_duplicates(inplace=True)

# Ensure there are no null values in critical columns
logging.info("Checking for missing values in the dataset:")
missing_data = weather_data.isnull().sum()
logging.info(f"Missing data by column:\n{missing_data}")

# Drop rows with missing date, city, or temperature data
weather_data.dropna(subset=['date', 'city', 'max_temp', 'min_temp', 'avg_temp', 'humidity', 'precipitation'], inplace=True)

# Ensure the 'date' column is in the correct format (DD/MM/YYYY HH:MM)
# Use a format string that matches the pattern in your data ('%d/%m/%Y %H:%M')
weather_data['date'] = pd.to_datetime(weather_data['date'], format='%d/%m/%Y %H:%M', errors='coerce')

# Log any invalid dates (rows with NaT in 'date' column)
invalid_dates = weather_data[weather_data['date'].isnull()]
if not invalid_dates.empty:
    logging.error(f"Rows with invalid date values:\n{invalid_dates}")
    weather_data.dropna(subset=['date'], inplace=True)  # Remove rows with invalid dates

# Clean up any extra spaces in city names or other categorical columns
weather_data['city'] = weather_data['city'].str.strip()

# Verify if the dataset has been cleaned up (no null values and invalid dates)
logging.info(f"Data after cleaning (missing values check):")
missing_data_after = weather_data.isnull().sum()
logging.info(f"Missing data by column:\n{missing_data_after}")

# Inspect the cleaned dataset
logging.info("Cleaned dataset preview:")
logging.info(weather_data.head())

# Save the cleaned data to a new CSV file
output_file_path = 'cleaned_weather_data.csv'
weather_data.to_csv(output_file_path, index=False)
logging.info(f"Cleaned data saved to {output_file_path}.")
