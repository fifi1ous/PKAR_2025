import pandas as pd

# Load the eclipse data CSV file
# This file should contain columns: lat, long, max_time_utc (UTC time of max eclipse), magnitude
df = pd.read_csv("centroids_magnitude.csv")

# Convert the 'max_time_utc' column to datetime objects (timezone-aware in UTC)
# This handles both formats with and without fractional seconds
df['max_time_utc'] = pd.to_datetime(df['max_time_utc'], utc=True)

# Extract the decimal hour from the datetime
# For example, 18:45:00 becomes 18.75
# The formula includes hours + minutes/60 + seconds/3600 + microseconds/3_600_000_000
df['hour'] = (
    df['max_time_utc'].dt.hour +
    df['max_time_utc'].dt.minute / 60 +
    df['max_time_utc'].dt.second / 3600 +
    df['max_time_utc'].dt.microsecond / 3_600_000_000
)

# Round the decimal hour to 2 decimal places (optional, for readability)
df['hour'] = df['hour'].round(2)

# Extract time as a formatted string (HH:MM) for easier human interpretation
df['hour_min'] = df['max_time_utc'].dt.strftime('%H:%M')

# Save the modified DataFrame to a new CSV file
# The output includes the original columns plus 'hour' and 'hour_min'
df.to_csv("centroids_time3.csv", index=False)

# Inform the user that the file was saved successfully
print("Saved to 'centroids_time3.csv'")
