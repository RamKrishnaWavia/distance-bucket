import pandas as pd
from geopy.distance import geodesic
import streamlit as st
import io
import itertools  # Import itertools

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


def process_drop_points(df):  # No reference coords anymore.
    """
    Processes drop points from a DataFrame, calculates distances *between all points*,
    and categorizes them into distance buckets.

    Args:
        df: DataFrame containing drop point data.

    Returns:
        A DataFrame with a 'Distance Bucket' column, or None on error.
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


        # --- Calculate distances between all *pairs* of points ---
        distances = []
        for index1, row1 in df.iterrows():
            for index2, row2 in df.iterrows():  # Iterate through *all* pairs
                if index1 != index2:  # Don't calculate distance to itself
                    dist = calculate_distance(row1[lat_column], row1[lon_column], row2[lat_column], row2[lon_column])
                    if dist is not None:
                        distances.append((row1['drop point ID'], row2['drop point ID'], dist)) #Store by ID

        # Create a dictionary to store distances for each drop point
        drop_point_distances = {}
        for dp1_id, dp2_id, dist in distances:
            if dp1_id not in drop_point_distances:
                drop_point_distances[dp1_id] = []
            if dp2_id not in drop_point_distances:
                drop_point_distances[dp2_id] = []
            drop_point_distances[dp1_id].append(dist)
            drop_point_distances[dp2_id].append(dist)

        # --- Categorize distances into buckets for each drop point ---
        distance_buckets = {}
        for dp_id, dist_list in drop_point_distances.items():
            # average distance for the drop point to all other points.
            avg_distance = sum(dist_list) / len(dist_list)
            distance_buckets[dp_id] = categorize_distance(avg_distance)
        # Add a 'Distance Bucket' column to the DataFrame.
        df['Distance Bucket'] = df['drop point ID'].map(distance_buckets)

        return df

    except (IndexError, KeyError) as e:  # More specific exception handling
        st.error(f"Error: Could not find the required column: {e}")
        return None
    except ValueError as e:
        st.error(f"Error: Latitudes or Longitudes could not be converted to numeric data: {e}")
        return None


def create_input_template(file_name="drop_point_template.csv"):  # Corrected Function signature
    """
    Creates and provides a downloadable CSV template with example data.

    Args:
        file_name: The name of the template CSV file.
    """
    columns = [
        "city name",
        "society ID",
        "society name",
        "drop point ID",
        "drop point name",
        "drop point lat",
        "drop long"
    ]

    sample_data = {
        "city name": "Bangalore",
        "society ID": 12345,
        "society name": "Example Society",
        "drop point ID": 1,
        "drop point name": "Gate 1",
        "drop point lat": 12.9716,  # Example latitude
        "drop long": 77.5946   # Example longitude
    }

    df = pd.DataFrame([sample_data], columns=columns)

    # Create a buffer in memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # Convert buffer to bytes
    b = bytes(csv_buffer.getvalue().encode())


    # Use st.download_button to create the download link
    st.sidebar.download_button(
        label="Download Input Template",
        data=b,
        file_name=file_name,
        mime="text/csv"
    )
    st.sidebar.write("Populate the downloaded CSV with your data and upload it.")


# --- Streamlit App ---

st.title("Drop Point Distance Calculator")

# --- 1. Downloadable template in the sidebar ---
create_input_template() # call function here

# --- 2. Upload CSV --- (file uploader in sidebar, below the download template button)
st.sidebar.header("Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])



# --- 4. Process Data (if file uploaded and coordinates entered) ---
if uploaded_file is not None :
    try:
        df = pd.read_csv(uploaded_file)
        # Process the DataFrame
        processed_df = process_drop_points(df.copy())  # Pass a copy to avoid modifying the original
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
