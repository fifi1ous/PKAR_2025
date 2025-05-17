"""
This script downloads JSON data from the Mapotic public API (Rise hvězd),
filters observatories by specific types, and exports relevant location
data (name, latitude, longitude) to a CSV file.

Specifically, it looks for attributes with ID 38362 and values indicating:
  - fvze
  - wldd
  - wzeh
which represent selected observatory types.

Output:
    A CSV file named 'filtered_places.csv' with observatory name and coordinates.
"""

import json
import csv
import requests
import os

# === Step 1: Download JSON data from Mapotic ===

response = requests.get('https://www.mapotic.com/rise-hvezd/opendata.json')
response.raise_for_status()  # Raise an error if download fails

# Save raw JSON to temporary file
with open('data.json', 'w', encoding='utf-8') as f:
    f.write(response.text)

# === Step 2: Load JSON data ===

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# === Step 3: Define accepted observatory types ===

# Only keep places with these attribute values (attribute_id = 38362)
valid_types = {"fvze", "wldd", "wzeh"}

filtered = []  # List to store filtered observatories

# === Step 4: Filter observatories by type ===

for place in data['places']:
    name = place.get('name')
    lat = place.get('lat')
    lng = place.get('lng')

    # Get type identifiers from custom attributes
    type_ids = []
    for attr in place.get('attributes', []):
        if attr['attribute_id'] == 38362:
            value = attr['value']
            if isinstance(value, list):
                type_ids.extend(value)
            else:
                type_ids.append(value)

    # Check if any of the type IDs match the valid set
    if any(type_id in valid_types for type_id in type_ids):
        filtered.append({
            'name': name,
            'lat': lat,
            'lng': lng
        })

# === Step 5: Export filtered data to CSV ===

with open('filtered_places.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'lat', 'lng'])
    writer.writeheader()
    writer.writerows(filtered)

# === Step 6: Clean up temporary JSON file ===

os.remove('data.json')

# Done!
print("Export hotový: filtered_places.csv")
