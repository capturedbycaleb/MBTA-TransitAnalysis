import requests
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Configuration ---
# Your API Key (ensure this is handled securely in a real application)
apiKey = "68b143c7928743bfbf721868967a0a2c"
# MBTA Green Line B-branch
routeId = "Green-B"
# 1: toward Gov Center, 0: toward Boston College (Inbound/Outbound)
directionId = 0
# Base URL for the MBTA V3 API predictions endpoint
apiUrl = "https://api-v3.mbta.com/predictions"

# Dictionary of each stop's ID and name (Green-B stops, BC-bound direction)
stopDict = {
    "place-gover": 'Government Center',
    "place-pktrm": 'Park Street',
    "place-boyls": 'Boylston',
    "place-armnl": 'Arlington',
    "place-coecl": 'Copley',
    "place-hymnl": 'Hynes Convention Center',
    "place-kencl": 'Kenmore',
    "place-bland": 'Blandford Street',
    "place-buest": 'Boston University East',
    "place-bucen": 'Boston University Central',
    "place-amory": 'Amory Street',
    "place-babck": 'Babcock Street',
    "place-brico": 'Packards Corner',
    "place-harvd": 'Harvard Avenue',
    "place-grigg": 'Griggs Street',
    "place-alsgr": 'Allston Street',
    "place-wrnst": 'Warren Street',
    "place-wascm": 'Washington Street',
    "place-sthld": 'Sutherland Road',
    "place-chswk": 'Chiswick Road',
    "place-chill": 'Chestnut Hill Avenue',
    "place-sougr": 'South Street',
    "place-lake": 'Boston College'
}

# ----------------------------------------------------------------------
# ## Data Retrieval and Processing Functions
# ----------------------------------------------------------------------

def get_next_arrivals(stop_id: str, route_id: str, direction_id: int, api_key: str, api_url: str):
    """
    Fetches arrival predictions for a specific stop and calculates minutes until arrival.

    Arguments:
      - stop_id: station id (e.g., "place-pktrm")
      - route_id: MBTA route id (e.g., "Green-B")
      - direction_id: Direction of the line (0 or 1)
      - api_key: Your MBTA V3 API key
      - api_url: Base URL for the predictions endpoint

    Returns:
        List of minutes until next arrivals (int) or None if no valid predictions are found.
    """
    params = {
        "filter[route]": route_id,
        "filter[stop]": stop_id,
        "filter[direction_id]": direction_id
    }
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    try:
        # 1. Make the API request
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request error for stop {stop_id}: {e}")
        return None

    predictions = []

    if not data or "data" not in data or not data["data"]:
        return None

    # Iterate through each prediction in the response
    for prediction in data["data"]:
        attributes = prediction.get("attributes")
        arrival_iso = attributes.get("arrival_time")

        if not arrival_iso:
            continue

        try:
            # Clean up arrival time as it is returned in ISO format (removing colon from timezone offset)
            iso_no_colon = arrival_iso[:-3] + arrival_iso[-2:]
            # Parse the arrival time with timezone information
            arrival_time = datetime.datetime.strptime(
                iso_no_colon,
                "%Y-%m-%dT%H:%M:%S%z"
            )

            # Get current time with the same timezone info as the arrival time
            now = datetime.datetime.now(arrival_time.tzinfo)

            # Calculate time until next arrival (a timedelta object)
            time_until_arrival = arrival_time - now

            # Convert to total minutes
            minutes_until = int(time_until_arrival.total_seconds() / 60)

            # Only add arrivals that have yet to happen (>= 0 minutes)
            if minutes_until >= 0:
                predictions.append(minutes_until)
        except ValueError as e:
            print(f"Error parsing date/time for stop {stop_id}: {e}")
            continue

    return predictions if predictions else None

def calculate_wait_times(predictions: list):
    """
    Creates a list of wait times (intervals) between consecutive arrivals.

    Args:
        predictions: List of minutes until next arrivals.

    Returns:
        List of wait times (in minutes) or None if there are fewer than two predictions.
    """
    if predictions and len(predictions) > 1:
        # Sort predictions to ensure they are in chronological order (should be, but a safeguard)
        predictions.sort()
        # Calculate the difference between consecutive arrival times
        # wait time = time_to_arrival[i+1] - time_to_arrival[i]
        list_of_wait_times = [
            predictions[i+1] - predictions[i]
            for i in range(len(predictions) - 1)
        ]
        return list_of_wait_times
    else:
        # Not enough data (requires at least two predictions to calculate a wait time)
        return None

# ----------------------------------------------------------------------
# ## Statistical Analysis Functions
# ----------------------------------------------------------------------

def find_mean_time(list_of_times: list):
    """
    Finds the mean of a list of times using NumPy.

    Args:
        list_of_times: List of times (e.g., wait times).

    Returns:
        Mean value of times (float) or 0 if the list is empty.
    """
    return np.mean(list_of_times) if list_of_times else 0.0

def find_median_time(list_of_times: list):
    """
    Finds the median of a list of times using NumPy.

    Args:
        list_of_times: List of times (e.g., wait times).

    Returns:
        Median value of times (float) or 0 if the list is empty.
    """
    return np.median(list_of_times) if list_of_times else 0.0

def find_st_dev_time(list_of_times: list):
    """
    Finds the standard deviation of a list of times using NumPy.

    Args:
        list_of_times: List of times (e.g., wait times).

    Returns:
        Standard deviation value of times (float) or 0 if the list is empty.
    """
    return np.std(list_of_times) if list_of_times else 0.0

# ----------------------------------------------------------------------
# ## Main Execution and Data Aggregation
# ----------------------------------------------------------------------

def gather_station_wait_data(stop_dict: dict, route_id: str, direction_id: int, api_key: str, api_url: str):
    """
    Iterates through all stations, retrieves predictions, calculates statistics,
    and aggregates the data into a DataFrame.

    Arguments:
      - stop_dict: Dictionary of station IDs and names.
      - route_id: MBTA route id.
      - direction_id: Direction of the line.
      - api_key: Your MBTA V3 API key.
      - api_url: Base URL for the predictions endpoint.

    Returns:
        A pandas DataFrame containing station, mean, median, and stdev wait times.
    """
    all_station_data = []

    # Using the dictionary of stops, iterates through each station ID and name
    for stop_id, name in stop_dict.items():
        all_predictions = get_next_arrivals(stop_id, route_id, direction_id, api_key, api_url)
        wait_times = calculate_wait_times(all_predictions)

        # Calculate statistics
        mean_wait_time = find_mean_time(wait_times)
        median_wait_time = find_median_time(wait_times)
        st_dev_time = find_st_dev_time(wait_times)

        # Print detailed data for user review
        if wait_times is not None and len(wait_times) > 0:
            print(f"{name} Mean wait time: {mean_wait_time:.2f} Minutes, Median wait time: {median_wait_time:.2f} Minutes, Standard Deviation: {st_dev_time:.2f}")
        else:
            print(f"No valid wait time data (fewer than 2 predictions) for {name}.")
        print("---------------------------------------------------------------------------------------------------------")

        # Aggregate data
        all_station_data.append({
            'Station': name,
            'Mean Wait Time': mean_wait_time,
            'Median Wait Time': median_wait_time,
            'Standard Deviation': st_dev_time,
            'Data Available': wait_times is not None and len(wait_times) > 0
        })

    # Create a DataFrame for easier handling and filtering
    return pd.DataFrame(all_station_data)

# ----------------------------------------------------------------------
# ## Visualization Function
# ----------------------------------------------------------------------

def plot_wait_times(df: pd.DataFrame, time_column: str, title: str, filename: str):
    """
    Generates and saves a bar chart of wait times per station.

    Arguments:
        df: DataFrame containing the station data.
        time_column: The column name to plot (e.g., 'Mean Wait Time').
        title: Title of the chart.
        filename: Name for the saved image file.
    """
    # Filter for stations where data was available
    df_plot = df[df['Data Available'] == True]

    if df_plot.empty:
        print("Cannot plot: No stations had valid wait time data.")
        return

    plt.figure(figsize=(12, 7))  # Increase size for better readability
    plt.bar(df_plot['Station'], df_plot[time_column], color='#008000', alpha=0.8) # Use a darker Green
    plt.xlabel('Station', fontsize=12)
    plt.ylabel(f'{time_column} (minutes)', fontsize=12)
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, ha='right')  # Rotate station names for readability
    plt.grid(axis='y', linestyle='--', alpha=0.6) # Add grid lines for better value comparison
    plt.tight_layout()  # Prevents labels from being cut off
    plt.savefig(filename)  # Save the figure
    plt.show()  # Display the figure

# ----------------------------------------------------------------------
# ## Main Script Execution
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # Gather and process all station data
    station_data_df = gather_station_wait_data(
        stopDict,
        routeId,
        directionId,
        apiKey,
        apiUrl
    )

    # Visualize the Mean Wait Times
    plot_wait_times(
        station_data_df,
        time_column='Mean Wait Time',
        title='Average Wait Times at Green Line B-Branch Stations',
        filename='mean_wait_times_bar.png'
    )