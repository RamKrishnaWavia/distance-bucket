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

# --- 3. Input Reference Coordinates ---
st.sidebar.header("Enter Reference Coordinates")
reference_latitude = st.sidebar.number_input("Reference Latitude", min_value=-90.0, max_value=90.0, value=12.9392379)
reference_longitude = st.sidebar.number_input("Reference Longitude", min_value=-180.0, max_value=180.0, value=77.7289339)

# --- 4. Process Data (if file uploaded and coordinates entered) ---
if uploaded_file is not None and reference_latitude is not None and reference_longitude is not None:
    try:
        df = pd.read_csv(uploaded_file)
        # Get unique city names
        if 'city name' not in df.columns:
            st.error("Error: 'city name' column not found.  Please ensure it exists in your CSV.")
        else:
            cities = df['city name'].unique()
            all_processed_dfs = {} # Store all DataFrames

            for city in cities:
                city_df = df[df['city name'] == city].copy() # Filter for current city.  Use .copy() to avoid SettingWithCopyWarning
                processed_df = process_drop_points(city_df, reference_latitude, reference_longitude)
                if processed_df is not None:  # Check if process_drop_points() was successful.
                    all_processed_dfs[city] = processed_df # Store processed df by city
            # --- Display Results ---
            if all_processed_dfs: # if data processed.
                for city, processed_df in all_processed_dfs.items():
                    st.subheader(f"Processed Data for {city}")
                    st.dataframe(processed_df)
                    st.subheader(f"Distance Bucket Counts for {city}")
                    st.write(processed_df['Distance Bucket'].value_counts()) # Print counts
                # --- Download Button for Results (Combined) ---
                # Combine all dataframes.
                combined_df = pd.concat(all_processed_dfs.values(), ignore_index=True)
                csv_buffer = io.StringIO()
                combined_df.to_csv(csv_buffer, index=False)
                b = bytes(csv_buffer.getvalue().encode()) # convert the text data to bytes
                st.download_button(
                    label="Download Processed Data (All Cities) as CSV",
                    data=b,
                    file_name="processed_drop_points_all.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data could be processed.  Check your CSV data and coordinates.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
