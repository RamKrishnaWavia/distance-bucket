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
SID_002,28.6711,77.3302
SID_003,28.667,77.4784
"""

st.subheader("Input Data")

col1, col2 = st.columns(2)

with col1:
    st.write("Option 1: Paste your data")
    text_input = st.text_area(
        "Paste data here (Society ID, Latitude, Longitude)",
        value=sample_data,
        height=250,
        help="Each line should contain Society ID, Latitude, and Longitude, separated by commas."
    )

with col2:
    st.write("Option 2: Upload a CSV file")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="The CSV should have columns: 'Society ID', 'Latitude', 'Longitude'"
    )


if uploaded_file is not None or text_input:
    try:
        if uploaded_file is not None:
            # If a file is uploaded, use it
            df = pd.read_csv(uploaded_file)
            # Standardize column names
            df.columns = ['Society ID', 'Latitude', 'Longitude']
        else:
            # Otherwise, use the text input
            data = io.StringIO(text_input)
            df = pd.read_csv(data, header=None, names=['Society ID', 'Latitude', 'Longitude'])

        # --- Data Processing ---

        # 1. Calculate distances
        df['Distance (km)'] = calculate_distances(df)

        # 2. Bucketize distances
        df['Distance Bucket'] = df['Distance (km)'].apply(bucketize_distance)

        # --- Display Results ---
        st.subheader("Processed Data with Distances and Buckets")
        st.dataframe(df)

        st.subheader("Summary of Distance Buckets")

        # Define the desired order for the buckets
        bucket_order = [
            "> 5 km",
            "4 - 5 km",
            "3 - 4 km",
            "2 - 3 km",
            "1 - 2 km",
            "< 1 km",
        ]

        # Calculate bucket counts
        bucket_counts = df['Distance Bucket'].value_counts().reindex(bucket_order).fillna(0).astype(int)

        st.table(bucket_counts)


    except Exception as e:
        st.error(f"An error occurred while processing the data. Please check the format.")
        st.error(f"Error details: {e}")
