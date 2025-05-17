"""
Visual Analysis of Light Pollution in European Capital Cities (2014–2024)

This script:
- Loads light pollution data from a CSV file
- Computes normalized pollution levels per square meter
- Plots trends for top-emitting cities, Prague, and other EU capitals
- Visualizes 2024 city averages in a polar chart

Required libraries: csv, numpy, pandas, matplotlib
"""

import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Data Loading and Preprocessing ---

# Dictionaries to store processed data:
# - LP_C_EU_meter: normalized pollution per m² per city across years
# - LP_C_EU_2024: absolute pollution for 2024
LP_C_EU_meter = {}
LP_C_EU_2024 = {}

# Load CSV and process rows
with open('Capital_EU.csv', newline='', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)  # Skip header

    for row in reader:
        country = row[1]
        row_meter = []

        # Normalize values by city area (in row[2])
        for i in range(3, len(row)):
            row_meter.append(float(row[i]) / float(row[2]))

        LP_C_EU_meter[country] = row_meter
        LP_C_EU_2024[country] = float(row[-1])  # 2024 value

# --- Visualization Settings ---

# Custom colors for dark background
dark_grey = '#2b2b2b'
text_color = 'white'
grid_color = '#444444'
legend_bg_color = '#5a5a5a'

# Years of data
x = range(2014, 2025)

# Top 6 country colors (colorblind-friendly)
top_colors = ['#1f77b4', '#2ca02c', '#d62728',
              '#9467bd', '#8c564b', '#17becf']
prague_color = '#FFA500'

# --- Top Emitters and Statistics ---

# Compute average pollution for each city
averages = {country: np.mean(data) for country, data in LP_C_EU_meter.items()}
sorted_countries = sorted(averages, key=averages.get, reverse=True)

# Select top 6 countries
top_countries = sorted_countries[:6]

# Include Prague explicitly
plot_countries = top_countries.copy()
if 'Prague' not in plot_countries:
    plot_countries.append('Prague')

# Other cities (excluding top and Prague)
excluded = set(plot_countries)
rest_countries = [c for c in LP_C_EU_meter if c not in excluded]

# Compute min/max across other cities
rest_data_matrix = np.array([LP_C_EU_meter[country] for country in rest_countries])
min_rest = np.min(rest_data_matrix, axis=0)
max_rest = np.max(rest_data_matrix, axis=0)

def setup_dark_axes(ax):
    """Set dark-themed axes for plots."""
    ax.set_facecolor(dark_grey)
    ax.tick_params(colors=text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.title.set_color(text_color)
    ax.grid(color=grid_color)

# --- Plot Top 6, Prague, and Range of Others ---

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor(dark_grey)

# Plot top emitters
for i, country in enumerate(top_countries):
    ax.plot(x, LP_C_EU_meter[country], label=country, color=top_colors[i], linewidth=2)

# Highlight Prague
if 'Prague' in LP_C_EU_meter:
    ax.plot(x, LP_C_EU_meter['Prague'], label='Prague', color=prague_color, linewidth=2)

# Plot min and max values for rest of cities
ax.plot(x, min_rest, label='Minimum of the rest of the cities (Sofia)', color='white', linestyle='--')
ax.plot(x, max_rest, label='Maximum of the rest of the cities (Helsinki)', color='white', linestyle='-.')

# Configure axis and legend
ax.set_title('Light Pollution in EU Cities (2014–2024): Top Emitters, Extremes of Remaining Cities, and Prague')
ax.set_xlabel('Year')
ax.set_ylabel('Light Pollution (nW/cm²·sr) per m² of City Area')
ax.set_xticks(x)
setup_dark_axes(ax)
ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5), facecolor=legend_bg_color, edgecolor=legend_bg_color, fontsize='small')
plt.tight_layout()
plt.show()

# --- Plot Remaining Cities in Two Groups ---

# Split other cities into two halves for readability
mid = len(other_countries) // 2
other_first_half = other_countries[:mid]
other_second_half = other_countries[mid:]

# Determine Y-axis limits with padding
all_other_values = [value for country in other_countries for value in LP_C_EU_meter[country]]
ymin = min(all_other_values)
ymax = max(all_other_values)
padding = (ymax - ymin) * 0.05
ymin -= padding
ymax += padding

# Plot group 1
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor(dark_grey)
for country in other_first_half:
    ax.plot(x, LP_C_EU_meter[country], label=country)

ax.set_title('Other EU Capital Cities (Group 1)')
ax.set_xlabel('Year')
ax.set_ylabel('Metered Data')
ax.set_xticks(x)
ax.set_ylim(ymin, ymax)
setup_dark_axes(ax)
ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5), facecolor=legend_bg_color, edgecolor=legend_bg_color, fontsize='small')
plt.tight_layout()
plt.show()

# Plot group 2
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor(dark_grey)
for country in other_second_half:
    ax.plot(x, LP_C_EU_meter[country], label=country)

ax.set_title('Other EU Capital Cities (Group 2)')
ax.set_xlabel('Year')
ax.set_ylabel('Metered Data')
ax.set_xticks(x)
ax.set_ylim(ymin, ymax)
setup_dark_axes(ax)
ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5), facecolor=legend_bg_color, edgecolor=legend_bg_color, fontsize='small')
plt.tight_layout()
plt.show()

# --- Polar Chart for 2024 Averages ---

# Create dataframe sorted by 2024 values
df = pd.DataFrame(LP_C_EU_2024.items(), columns=["Name", "Value"])
df = df.sort_values(by="Value")

# Visualization parameters
upperLimit = 100
lowerLimit = 30
labelPadding = 4
bar_color = '#61a4b2'
text_color = 'black'

# Normalize bar heights
max_val = df["Value"].max()
slope = (upperLimit - lowerLimit) / max_val
heights = slope * df["Value"] + lowerLimit

# Polar coordinate calculations
width = 2 * np.pi / len(df.index)
indexes = list(range(len(df.index)))
angles = [index * width for index in indexes]

# Create polar plot
plt.figure(figsize=(20, 10))
ax = plt.subplot(111, polar=True)
ax.set_facecolor('none')
plt.axis('off')

# Draw bars
bars = ax.bar(
    x=angles,
    height=heights,
    width=width,
    bottom=lowerLimit,
    linewidth=2,
    edgecolor='none',
    color=bar_color,
)

# Add city labels around the circle
for bar, angle, height, label in zip(bars, angles, heights, df["Name"]):
    rotation = np.rad2deg(angle)
    if np.pi/2 <= angle < 3*np.pi/2:
        alignment = "right"
        rotation += 180
    else:
        alignment = "left"

    ax.text(
        x=angle,
        y=lowerLimit + height + labelPadding,
        s=label,
        ha=alignment,
        va='center',
        rotation=rotation,
        rotation_mode="anchor",
        fontsize=9,
        color=text_color
    )

# Finalize and export
plt.tight_layout()
ax.set_title("Average Light Pollution Contribution by EU Cities (2024)", color=text_color, fontsize=16)
plt.savefig("light_pollution_chart.svg", format="svg", transparent=True)
plt.show()
