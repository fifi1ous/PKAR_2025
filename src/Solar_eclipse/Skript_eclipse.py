"""
This script estimates the occurrence and rough magnitude of a solar eclipse on August 12, 2026,
for a list of geographic locations provided in a CSV file. It uses Skyfield for astronomical 
calculations and outputs the eclipse time and estimated magnitude for each location.

Input: 
    - CSV file 'Centr_Europe.csv' with columns 'Lat' and 'Long' (semicolon-separated)

Output:
    - CSV file 'eclipse_2026_output.csv' with added columns:
        'ECLIPSE_TIME'      (UTC time of maximum eclipse if visible)
        'ECLIPSE_MAGNITUDE' (Approximate magnitude, rough proxy based on Sun-Moon distance)
"""

import pandas as pd
from skyfield.api import load, wgs84
from datetime import datetime, timedelta
from skyfield.almanac import find_discrete, solar_eclipses
import numpy as np

# Load input CSV containing latitude and longitude points
df = pd.read_csv("Centr_Europe.csv", sep=';')  # Update this filename if necessary

# Load ephemeris data from Jet Propulsion Laboratory (JPL)
eph = load('de421.bsp')
sun, earth, moon = eph['sun'], eph['earth'], eph['moon']
ts = load.timescale()

# Define the time window to search for the eclipse event (in UTC)
start_time = ts.utc(2026, 8, 12, 15)
end_time = ts.utc(2026, 8, 12, 20)

# Lists to hold eclipse results
eclipse_times = []
eclipse_magnitudes = []

# Function to estimate eclipse time and magnitude for a given location
def estimate_eclipse(lat, lon):
    """
    Checks whether a solar eclipse is visible at the given lat/lon between start_time and end_time.
    If visible, returns the time of maximum eclipse and an approximate magnitude proxy.

    Parameters:
        lat (float): Latitude in degrees
        lon (float): Longitude in degrees

    Returns:
        eclipse_time (str or None): ISO UTC time of eclipse maximum
        magnitude (float): Rough eclipse magnitude (proxy based on Sun-Moon distance)
    """
    observer = wgs84.latlon(lat, lon)
    t0, t1 = start_time, end_time

    # Find solar eclipse events in the given time window
    times, events = find_discrete(t0, t1, solar_eclipses(eph, observer))
    
    if len(events) == 0:
        return None, 0.0  # No eclipse at this location

    for ti, ei in zip(times, events):
        if ei == 1:  # 1 indicates maximum eclipse
            # Only consider eclipse if the Sun is above the horizon
            astrometric = observer.at(ti).observe(sun).apparent()
            sun_alt = astrometric.altaz()[0].degrees
            if sun_alt > 0:
                # Approximate eclipse magnitude based on Sun-Moon distance
                sun_pos = observer.at(ti).observe(sun).apparent().position.km
                moon_pos = observer.at(ti).observe(moon).apparent().position.km
                distance = np.linalg.norm(np.array(sun_pos) - np.array(moon_pos))
                mag = max(0, 1 - distance / 10000)  # crude proxy for overlap
                return ti.utc_iso(), round(mag, 3)
    
    return None, 0.0  # No visible eclipse

# Loop through all locations in the CSV
for idx, row in df.iterrows():
    lat = row['Lat']
    lon = row['Long']
    time, mag = estimate_eclipse(lat, lon)
    eclipse_times.append(time)
    eclipse_magnitudes.append(mag)

# Add results to DataFrame
df['ECLIPSE_TIME'] = eclipse_times
df['ECLIPSE_MAGNITUDE'] = eclipse_magnitudes

# Save output CSV with eclipse data
df.to_csv("eclipse_2026_output.csv", sep=';', index=False)
print("Done. Results saved to 'eclipse_2026_output.csv'")
