"""
This script reads geographic observation data from a CSV file, computes sunset and dusk times 
for each location on a specified target date using the Astral library, and determines whether 
each observation occurred before dusk. It then writes the results, including visibility, to a new CSV.

Expected input CSV structure:
    Latitude, Longitude, ..., Magnitude, VisibilityCheckTime, ObservationTime

Output CSV includes:
    Latitude, Longitude, Magnitude, Time, Sunset (decimal), Dusk (decimal), Visible (bool)
"""

from astral import LocationInfo
from astral.sun import sun
import datetime
import csv

# Converts a datetime object to decimal hours (e.g., 18.5 = 18:30)
def to_decimal_hours(dt):
    return dt.hour + dt.minute / 60 + dt.second / 3600

# Input and output file paths
input_file = "centroids_time3.csv"
output_file = "centroids_magnitude.csv"

# Lists to store parsed and computed data
latitudes = []
longitudes = []
visible = []
sunset = []
dusk = []
magn = []
time = []

# Date for which to compute sunset and dusk times
target_date = datetime.date(2026, 8, 12)

# Read input CSV file and calculate sun times and visibility
with open(input_file, newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row

    for row in reader:
        lat = float(row[0])
        lon = float(row[1])
        magnitude = float(row[3])  # Column 3: event magnitude
        observation_time = row[5]  # Column 5: observation time as a string

        # Create a location using latitude and longitude
        city = LocationInfo(latitude=lat, longitude=lon)

        try:
            # Get sun event times for the specified date in UTC
            s = sun(city.observer, date=target_date, tzinfo="UTC")
            sunset_decimal = to_decimal_hours(s['sunset'])
            dusk_decimal = to_decimal_hours(s['dusk'])
        except ValueError:
            # Sun data may not be available for polar night/day locations
            sunset_decimal = None
            dusk_decimal = None

        # Determine if the observation occurred before dusk
        if sunset_decimal is not None:
            # Column 4: observation time in decimal hours (float)
            visibility = float(row[4]) < dusk_decimal
        else:
            # Assume visibility if sun times are not computable (can change to None if needed)
            visibility = True

        # Append computed and input data to lists
        latitudes.append(lat)
        longitudes.append(lon)
        magn.append(magnitude)
        time.append(observation_time)
        sunset.append(sunset_decimal)
        dusk.append(dusk_decimal)
        visible.append(visibility)

# Write results to output CSV file
with open(output_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow(['Latitude', 'Longitude', 'Magnitude', 'Time', 'Sunset', 'Dusk', 'Visible'])
    # Write rows of computed data
    for i in range(len(magn)):
        writer.writerow([
            latitudes[i],
            longitudes[i],
            magn[i],
            time[i],
            sunset[i],
            dusk[i],
            visible[i]
        ])
