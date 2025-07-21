# Drop Point Distance Calculator - Streamlit App

## Overview

This Streamlit application allows you to calculate distances between drop points in a CSV file and categorize them into distance buckets based on a reference point.  It's designed to be user-friendly and easy to deploy on Streamlit Cloud.

## Features

*   **CSV Upload:** Upload your CSV file containing drop point data.
*   **Reference Point Input:** Enter the latitude and longitude of a reference point.
*   **Distance Calculation:** Calculates the distance (in kilometers) between each drop point and the reference point.
*   **Distance Bucketing:** Categorizes drop points into distance buckets (e.g., "< 1 km", "1 - 2 km", etc.).
*   **Data Display:** Displays the processed data in an interactive table.
*   **Download Results:** Provides a button to download the processed data in CSV format.
*   **Error Handling:** Includes robust error handling to gracefully manage common issues such as invalid data, missing columns, and file errors.

## Prerequisites

*   **Python 3.7+:** Ensure you have Python installed.
*   **pandas, geopy, and streamlit libraries:** These libraries will be installed automatically when you deploy the app using Streamlit Cloud, but you can install them locally using:

    ```bash
    pip install pandas geopy streamlit
    ```

## Usage

1.  **Prepare Your CSV:**
    *   Your CSV file must have columns named:
        *   `drop point name`
        *   `drop point lat`: Latitude of the drop point (numeric).
        *   `drop long`: Longitude of the drop point (numeric).
        *   *(Optional) Any other columns you wish to keep, as the app will preserve all your CSV columns.*
    *   Ensure the latitude and longitude values are numeric.
    *   Example CSV structure:
    ```csv
    city name,society ID,society name,drop point ID,drop point name,drop point lat,drop long, other_column
    Bangalore,12345,Example Society,1,Gate 1,12.9716,77.5946, some_data
    ...
    ```
2.  **Run the Streamlit App:**
    *   Save the Python code (e.g., `drop_point_app.py`) in a directory.
    *   Create a `requirements.txt` file in the same directory with the following content:

        ```
        pandas
        geopy
        streamlit
        ```

    *   Deploy the app to Streamlit Cloud (instructions below).
    *   **OR** Run the app locally:
        ```bash
        streamlit run drop_point_app.py
        ```
        This will open the app in your web browser.
3.  **Use the App:**
    *   Upload your CSV file using the file uploader in the sidebar.
    *   Enter the reference latitude and longitude in the sidebar.
    *   The processed data and distance bucket counts will be displayed.
    *   Click the "Download Processed Data as CSV" button to download the results.

## Deployment to Streamlit Cloud

1.  **Create a GitHub Repository (if you don't have one):** If you don't already have a GitHub account and repository, create one.
2.  **Push Your Files to GitHub:**  Upload your `.py` file and `requirements.txt` file to your GitHub repository.
3.  **Deploy to Streamlit Cloud:**
    *   Go to [https://streamlit.io/cloud](https://streamlit.io/cloud) and sign in.
    *   Click "New app."
    *   Choose your GitHub repository.
    *   Select the branch where your code is (usually `main` or `master`).
    *   Specify the path to your main `.py` file (e.g., `drop_point_app.py`).
    *   Click "Deploy!"

## Known Issues / Limitations

*   The app assumes the latitude and longitude columns are named exactly `"drop point lat"` and `"drop long"`.  Modify the code if your columns have different names.
*   Large CSV files may take some time to process.
*   Error handling is in place, but edge cases in your data could potentially still lead to unexpected behavior.  Thoroughly check your results.

## Contributing

Contributions are welcome!  Feel free to submit pull requests with improvements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE.md).  *(Create a LICENSE.md file with the content of the MIT License, if you want to be very thorough).*
