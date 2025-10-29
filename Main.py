#main.py
import requests
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Import modules from the same directory
import config
import mbta_api
import analysis

# ----------------------------------------------------------------------
# ## Main Execution and Data Aggregation
# ----------------------------------------------------------------------

def gather_station_wait_data():
    """
    Iterates through all stations, retrieves predictions, calculates statistics,
    and aggregates the data into a DataFrame.

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
        station_data_df = gather_station_wait_data(
        config.STOP_DICT, # Access the dictionary via the imported module name
        config.ROUTE_ID,
        config.DIRECTION_ID,
        config.API_KEY,
        config.API_URL
    )

    # Visualize the Mean Wait Times
    plot_wait_times(
        station_data_df,
        time_column='Mean Wait Time',
        title='Average Wait Times at Green Line B-Branch Stations',
        filename='mean_wait_times_bar.png'
    )