"""
This script enriches a list of observatories with geographic coordinates (latitude, longitude)
using geolocation services (OpenStreetMap/Nominatim and Wikipedia). It intelligently skips
space-based observatories and falls back on Wikipedia if standard geocoding fails.

Input:
    - CSV file named "observatories.csv" with at least columns 'name' and 'location'

Output:
    - CSV file "observatories_updated.csv" with added 'latitude' and 'longitude' columns
"""

import pandas as pd
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import wikipedia
import re

# === Load Data ===

# Load the input CSV file into a DataFrame
csv_file = "observatories.csv"  # Replace if necessary
df = pd.read_csv(csv_file)

# Add empty latitude and longitude columns to store results
df["latitude"] = None
df["longitude"] = None

# === Geolocation Setup ===

# Initialize Nominatim geolocator (based on OpenStreetMap)
geolocator = Nominatim(user_agent="observatory_locator")

# Add rate limiter to respect OpenStreetMap usage policy
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# === Space-Based Observatory Detection ===

# Keywords that imply the observatory is not Earth-based
space_keywords = ["space", "orbit", "l1", "sun-earth", "lagrange"]

def is_space_based(location):
    """
    Determine if the observatory is space-based based on keywords in the location description.
    """
    if isinstance(location, str):
        return any(keyword.lower() in location.lower() for keyword in space_keywords)
    return False

# === Wikipedia Coordinate Extraction ===

def get_coordinates_from_wikipedia(query):
    """
    Attempt to extract latitude and longitude from a Wikipedia page summary.
    Searches for coordinates in decimal degrees using regex.
    
    Returns:
        (latitude, longitude) as floats or (None, None) if not found.
    """
    try:
        page = wikipedia.page(query)
        # Match simple decimal degree coordinates
        coord_pattern = r"(\d{1,2}\.\d+)[° ]?[NS],?\s*(\d{1,3}\.\d+)[° ]?[EW]"
        match = re.search(coord_pattern, page.summary)
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            return lat, lon
    except Exception:
        return None, None
    return None, None

# === Geocode Each Observatory ===

for index, row in df.iterrows():
    try:
        if not is_space_based(row["location"]):
            # === First attempt: OpenStreetMap ===
            location = geocode(row["name"])
            if not location:
                location = geocode(row["location"])
            
            if location:
                df.at[index, "latitude"] = location.latitude
                df.at[index, "longitude"] = location.longitude
            else:
                # === Second attempt: Wikipedia ===
                lat, lon = get_coordinates_from_wikipedia(row["name"])
                if not lat or not lon:
                    lat, lon = get_coordinates_from_wikipedia(row["location"])
                
                if lat and lon:
                    df.at[index, "latitude"] = lat
                    df.at[index, "longitude"] = lon
                else:
                    print(f"Could not find coordinates for {row['name']}")
            
            # Be respectful of Wikipedia’s API rate limits
            time.sleep(1)
        else:
            print(f"Skipping space-based observatory: {row['name']}")
    
    except Exception as e:
        print(f"Error fetching coordinates for {row['name']}: {e}")

# === Save Output ===

# Write the updated DataFrame with coordinates to a new CSV
updated_csv_file = "observatories_updated.csv"
df.to_csv(updated_csv_file, index=False)

print(f"Updated CSV saved as {updated_csv_file}")
