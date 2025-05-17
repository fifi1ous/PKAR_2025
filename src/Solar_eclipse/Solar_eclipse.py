# Eclipse Magnitude Calculator for Geographic Coordinates
# --------------------------------------------------------
# This script calculates the maximum solar eclipse magnitude and time of greatest eclipse
# for a list of geographic locations (latitude, longitude) on 12 August 2026.
# It uses the Skyfield library to compute the apparent positions of the Moon and Sun
# and writes the results to a CSV file.

from skyfield.api import load, Topos
import numpy as np
from math import asin
import csv

# --- Constants ---
RADIUS_SUN_KM = 696_340    # Radius of the Sun in kilometers
RADIUS_MOON_KM = 1_737.4   # Radius of the Moon in kilometers

# --- Load ephemeris data and timescale ---
ts = load.timescale()                 # Skyfield timescale object
eph = load('de421.bsp')              # JPL DE421 planetary ephemeris
sun, moon, earth = eph['sun'], eph['moon'], eph['earth']

# --- Generate time window around expected eclipse (12 Aug 2026, 18:00 UTC ± 1 hour) ---
minutes = np.linspace(-60, 60, 1000)  # Time window in minutes around 18:00 UTC
times = ts.utc(2026, 8, 12, 18, minutes)

# --- Eclipse Calculation Function ---
def eclipse(minutes, times, location, sun, moon):
    """
    Computes the maximum eclipse time and magnitude for a given location.

    Args:
        minutes: Time offsets in minutes from center time.
        times: Time array (Skyfield Time objects).
        location: Skyfield observer location (Topos).
        sun, moon: Skyfield planetary objects.

    Returns:
        t_max_utc: Time of maximum eclipse in UTC datetime format.
        magnitude: Eclipse magnitude (0 to 1).
    """
    separations = []
    for t in times:
        obs = location.at(t)
        sun_app = obs.observe(sun).apparent()
        moon_app = obs.observe(moon).apparent()
        sep = sun_app.separation_from(moon_app).degrees
        separations.append(sep)

    min_idx = np.argmin(separations)
    t_max = times[min_idx]
    t_max_utc = t_max.utc_datetime()

    # Recalculate positions at time of greatest eclipse
    obs = location.at(t_max)
    sun_app = obs.observe(sun).apparent()
    moon_app = obs.observe(moon).apparent()
    d = sun_app.separation_from(moon_app).radians

    # Compute angular radii
    sun_distance_km = sun_app.distance().km
    moon_distance_km = moon_app.distance().km
    R_sun = asin(RADIUS_SUN_KM / sun_distance_km)
    R_moon = asin(RADIUS_MOON_KM / moon_distance_km)

    # Compute magnitude using eclipse geometry
    if d >= R_sun + R_moon:
        magnitude = 0.0  # No eclipse
    elif d <= abs(R_sun - R_moon):
        magnitude = min(R_moon, R_sun) / R_sun  # Full coverage (total or annular)
    else:
        chord = R_moon + R_sun - d
        magnitude = chord / (2 * R_sun)

    return t_max_utc, magnitude

# --- Optional: Convert split integer+decimal fields (not used in this code) ---
def decimal(row, a, b):
    """
    Converts two columns of integer and decimal parts into a float.

    Args:
        row: The current CSV row.
        a, b: Indexes of integer and decimal columns.

    Returns:
        full_number: Combined float number.
    """
    integer_part = int(row[a])
    decimal_part = int(row[b])
    decimal_length = len(row[b])
    if integer_part < 0:
        decimal_part *= -1
    return integer_part + decimal_part / (10 ** decimal_length)

# --- Read input CSV with semicolon-separated lon;lat values ---
filename = 'Centroids2.csv'
rows = []

with open(filename, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)  # Skip header row
    index = 1
    for row in reader:
        # Parse coordinates from single semicolon-separated cell
        lon_str, lat_str = row[0].split(';')
        lon = float(lon_str)
        lat = float(lat_str)

        print(index, lat, lon)
        index += 1

        # Create observer location
        location = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)

        # Compute eclipse time and magnitude
        time_max, magnitude = eclipse(minutes, times, location, sun, moon)

        # Store results
        rows.append([lat, lon, time_max, round(magnitude, 4)])

# --- Write results to output CSV ---
with open("centroids_magnitude.csv", 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['lat', 'long', 'max_time_utc', 'magnitude'])  # Header

    for row in rows:
        writer.writerow(row)
