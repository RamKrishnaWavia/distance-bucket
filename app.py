import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import io

def calculate_distances(df):
    """
    Calculates the distance between consecutive points in a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with 'Latitude' and 'Longitude' columns.

    Returns:
        list: A list of distances in kilometers. The first element is 0.
    """
    distances = [0.0]  # The first location has no preceding point
    for i in range(1, len(df)):
        # Get coordinates for the current and previous point
        point1 = (df['Latitude'].iloc[i-1], df['Longitude'].iloc[i-1])
        point2 = (df['Latitude'].iloc[i], df['Longitude'].iloc[i])

        # Calculate the distance and append to the list
        if pd.notna(point1[0]) and pd.notna(point1[1]) and pd.notna(point2[0]) and pd.notna(point2[1]):
            distance_km = geodesic(point1, point2).kilometers
            distances.append(distance_km)
        else:
            distances.append(0.0) # Handle cases with missing lat/lon
    return distances

def bucketize_distance(km):
    """
    Categorizes a distance in kilometers into predefined buckets.

    Args:
        km (float): The distance in kilometers.

    Returns:
        str: The corresponding distance bucket.
    """
    if km is None or km == 0:
        return "N/A"
    elif km < 1:
        return "< 1 km"
    elif 1 <= km < 2:
        return "1 - 2 km"
    elif 2 <= km < 3:
        return "2 - 3 km"
    elif 3 <= km < 4:
        return "3 - 4 km"
    elif 4 <= km < 5:
        return "4 - 5 km"
    else: # km >= 5
        return "> 5 km"

# --- Streamlit App ---

st.set_page_config(layout="wide")

st.title("Location Distance and Bucketing Tool")
st.write("Paste your location data below, including a 'Society ID', or upload a CSV file. The tool will calculate the distance between each consecutive point and categorize it into buckets.")

# Sample data to show the format
sample_data = """
SID_001,28.70232415,77.41863392
SID_001,28.6797132,77.3246482
SID_002,28.67619,77.31593
"""

st.subheader("Input Data")

col1, col2 = st.columns(2)

with col1:
    st.write("Option 1: Paste your data")
    # Use spaces as a separator to handle the new data format
    text_input = st.text_area(
        "Paste data here (Society ID, Latitude, Longitude)",
        value="3181 23.178967 72.628454\n3182 23.178967 72.628454",
        height=250,
        help="Each line should contain Society ID, Latitude, and Longitude, separated by spaces or commas."
    )

with col2:
    st.write("Option 2: Upload a CSV/Text file")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "txt"],
        help="The file should have columns: 'Society ID', 'Latitude', 'Longitude'"
    )


if uploaded_file is not None or text_input:
    try:
        if uploaded_file is not None:
            # If a file is uploaded, use it
            df = pd.read_csv(uploaded_file, header=None, delim_whitespace=True, names=['Society ID', 'Latitude', 'Longitude'])
        else:
            # Otherwise, use the text input
            data = io.StringIO(text_input)
            df = pd.read_csv(data, header=None, delim_whitespace=True, names=['Society ID', 'Latitude', 'Longitude'])

        # --- Data Processing ---

        # 1. Calculate distances
        df['Distance (km)'] = calculate_distances(df)
        df['Distance (km)'] = df['Distance (km)'].round(2) # Round for cleaner display

        # 2. Bucketize distances
        df['Distance Bucket'] = df['Distance (km)'].apply(bucketize_distance)

        # --- Display Results ---
        st.subheader("Processed Data with Distances and Buckets")
        st.write("Showing all rows. Non-zero distances indicate movement from the previous point.")
        st.dataframe(df)

        st.subheader("Summary of Distance Buckets (Only for Movements)")

        # Define the desired order for the buckets
        bucket_order = [
            "> 5 km",
            "4 - 5 km",
            "3 - 4 km",
            "2 - 3 km",
            "1 - 2 km",
            "< 1 km",
        ]

        # --- THIS IS THE KEY CHANGE ---
        # First, create a new DataFrame that ONLY includes rows where there was a move.
        moving_df = df[df['Distance (km)'] > 0]

        # Now, create the bucket counts from this filtered DataFrame.
        bucket_counts = moving_df['Distance Bucket'].value_counts().reindex(bucket_order).fillna(0).astype(int)

        st.table(bucket_counts)


    except Exception as e:
        st.error(f"An error occurred while processing the data. Please check your data format.")
        st.error(f"Error details: {e}")
