import pandas as pd
from geopy.distance import geodesic
import streamlit as st
import io

# --- Function Definitions ---

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the distance in kilometers between two points
    given their latitude and longitude.

    Args:
        lat1: Latitude of the first point.
        lon1: Longitude of the first point.
        lat2: Latitude of the second point.
        lon2: Longitude of the second point.

    Returns:
        The distance in kilometers.  Returns None if invalid coordinates.
    """
    try:
        return geodesic((lat1, lon1), (lat2, lon2)).km
    except (ValueError, TypeError) as e:  # Handles invalid coordinates and type errors
        # Consider more specific error handling, e.g., logging
        print(f"Warning: Invalid coordinates, could not calculate distance: {e}")
        return None

def categorize_distance(distance):
    """
    Categorizes a distance into a distance bucket.

    Args:
        distance: The distance in kilometers.

    Returns:
        A string representing the distance bucket.  Handles None (invalid data)
    """
    if distance is None:
        return "Invalid Coordinates"
    if distance < 1:
        return "< 1 km"
    elif 1 <= distance < 2:
        return "1 - 2 km"
    elif 2 <= distance < 3:
        return "2 - 3 km"
    elif 3 <= distance < 4:
        return "3 - 4 km"
    elif 4 <= distance < 5:
        return "4 - 5 km"
    else:
        return ">= 5 km"

def process_drop_points(df, reference_lat, reference_lon):
    """
    Processes drop points from a DataFrame, calculates distances, and categorizes
    them into distance buckets.

    Args:
        df: DataFrame containing drop point data.
        reference_lat: Latitude of the reference drop point.
        reference_lon: Longitude of the reference drop point.

    Returns:
        A DataFrame with distance and distance bucket columns, or None on error.
    """
    try:
        # Handle potential errors with column names
        lat_column = 'drop point lat'
        lon_column = 'drop long'
        if lat_column not in df.columns or lon_column not in df.columns:
            st.error("Error:  'drop point lat' and/or 'drop long' columns not found. Check column names.")
            return None

        # Convert the latitude and longitude columns to numeric, handling potential errors
        df[lat_column] = pd.to_numeric(df[lat_column], errors='coerce')  # Convert to numeric, coerce errors
        df[lon_column] = pd.to_numeric(df[lon_column], errors='coerce')

        # Remove rows with NaN values (which result from failed numeric conversion)
        df = df.dropna(subset=[lat_column, lon_column])

    except (IndexError, KeyError) as e:  # More specific exception handling
        st.error(f"Error: Could not find the required column: {e}")
        return None
    except ValueError as e:
        st.error(f"Error: Latitudes or Longitudes could not be converted to numeric data: {e}")
        return None


    # Calculate distances and create the distance bucket column
    df['Distance (km)'] = df.apply(lambda row: calculate_distance(reference_lat, reference_lon, row[lat_column], row[lon_column]), axis=1)
    df['Distance Bucket'] = df['Distance (km)'].apply(categorize_distance)

    return df


# --- Streamlit App ---

st.title("Drop Point Distance Calculator")

# --- 1. Upload CSV ---
st.sidebar.header("1. Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# --- 2. Input Reference Coordinates ---
st.sidebar.header("2. Enter Reference Coordinates")
reference_latitude = st.sidebar.number_input("Reference Latitude", min_value=-90.0, max_value=90.0, value=12.9392379)
reference_longitude = st.sidebar.number_input("Reference Longitude", min_value=-180.0, max_value=180.0, value=77.7289339)

# --- 3. Process Data (if file uploaded and coordinates entered) ---
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        # Process the DataFrame
        processed_df = process_drop_points(df.copy(), reference_latitude, reference_longitude)  # Pass a copy to avoid modifying the original
        if processed_df is not None:
            # --- Display Results ---
            st.subheader("Processed Data")
            st.dataframe(processed_df) # Use st.dataframe to render the DataFrame
            st.subheader("Distance Bucket Counts")
            st.write(processed_df['Distance Bucket'].value_counts())


            # --- Download Button for Results ---
            csv_buffer = io.StringIO()
            processed_df.to_csv(csv_buffer, index=False)
            # Convert the buffer to bytes
            b = bytes(csv_buffer.getvalue().encode())
            st.download_button(
                label="Download Processed Data as CSV",
                data=b,
                file_name="processed_drop_points.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
