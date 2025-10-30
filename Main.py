#main.py
import requests
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# Import modules from the same directory
import config
import mbta_api
import analysis

# ----------------------------------------------------------------------
# ## Main Execution and Data Aggregation
# ----------------------------------------------------------------------

def gather_station_wait_data(stop_dict: dict, route_id: str, direction_id: int, api_key: str, api_url: str):
    """
    Iterates through all stations, retrieves predictions, calculates statistics,
    and aggregates the data into a DataFrame.

    Returns:
        A pandas DataFrame containing station, mean, median, and stdev wait times.
    """
    all_station_data = []

    # Using the dictionary of stops, iterates through each station ID and name
    for stop_id, name in stop_dict.items():
        time.sleep(1.5)
        all_predictions = mbta_api.get_next_arrivals(stop_id, route_id, direction_id, api_key, api_url)
        wait_times = analysis.calculate_wait_times(all_predictions)

        # Calculate statistics
        mean_wait_time = analysis.find_mean_time(wait_times)
        median_wait_time = analysis.find_median_time(wait_times)
        st_dev_time = analysis.find_st_dev_time(wait_times)

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
    east_station_data_df = gather_station_wait_data(
        config.STOP_DICT, # Access the dictionary via the imported module name
        config.ROUTE_ID,
        config.EAST_DIRECTION_ID,
        config.API_KEY,
        config.API_URL
    )
    west_station_data_df = gather_station_wait_data(
        config.STOP_DICT, # Access the dictionary via the imported module name
        config.ROUTE_ID,
        config.WEST_DIRECTION_ID,
        config.API_KEY,
        config.API_URL
    )
    # Visualize the Mean Wait Times
    plot_wait_times(
        east_station_data_df,
        time_column='Mean Wait Time',
        title='Average Wait Times at Green Line B-Branch Stations',
        filename='mean_wait_times_bar.png'
    )
-----------------------------------------------------------------------
import requests
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # for visualizations

# --- Configuration ---
apiKey = "68b143c7928743bfbf721868967a0a2c"
routeId = "Green-B"
directionId = 1 # 1 means headed toward Gov Center, 0 means headed toward Boston College

#Dictionary of each stop's ID and name
stopDict = {
    "place-gover":'Government Center',
    "place-pktrm":'Park Street',
    "place-boyls":'Boylston',
    "place-armnl":'Arlington',
    "place-coecl":'Copley',
    "place-hymnl":'Hynes Convention Center',
    "place-kencl":'Kenmore',
    "place-bland":'Blandford Street',
    "place-buest":'Boston University East',
    "place-bucen":'Boston University Central',
    "place-amory":'Amory Street',
    "place-babck":'Babcock Street',
    "place-brico":'Packards Corner',
    "place-harvd":'Harvard Avenue',
    "place-grigg":'Griggs Street',
    "place-alsgr":'Allston Street',
    "place-wrnst":'Warren Street',
    "place-wascm":'Washington Street',
    "place-sthld":'Sutherland Road',
    "place-chswk":'Chiswick Road',
    "place-chill":'Chestnut Hill Avenue',
    "place-sougr":'South Street',
    "place-lake":'Boston College'
}

# Base URL for the MBTA V3 API predictions endpoint
apiUrl = "https://api-v3.mbta.com/predictions"

def getNextDeparture(stopId:str, name:str, direction:int):
    """
    Appends station name and time until next departure to a list

    Arugments:
      - stopId: station id
      - name: station name
      - direction: direction of line
    Returns: List of minutes until next departures
    """
    params = {
        # Filter by Route and Stop
        "filter[route]": routeId,
        "filter[stop]": stopId,
        "filter[direction_id]": directionId
    }
    headers = {}
    #Apply API key if present
    if apiKey:
        headers["X-API-Key"] = apiKey

    # 1. Make the API request and parse JSON (assuming success)
    response = requests.get(apiUrl, params=params, headers=headers)
    data = response.json()
    predictions = []

    #Ensures no error when there is no data
    if not data or "data" not in data or not data["data"]:
        return None

    numerates = data["data"]

    #Iterate through each set of attributes(each one contains a departure time)
    #Data structure: /data/{index}/attributes/departure_time
    for i in range(len(numerates)):
        attributes = numerates[i].get("attributes")
        departureIso = attributes.get("departure_time")

        #Ensures no error when there is no data
        if not departureIso:
            continue

        #Clean up departure time as it is returned in ISO
        isoNoColon = departureIso[:-3] + departureIso[-2:]
        departureTime = datetime.datetime.strptime(
            isoNoColon,
            "%Y-%m-%dT%H:%M:%S%z"
        )

        #Use datetime.now to find current time
        now = datetime.datetime.now(departureTime.tzinfo)

        #Calculate time until next departure
        timeUntilDeparture = departureTime - now

        #Convert to minutes
        minutesUntil = int(timeUntilDeparture.total_seconds() / 60)

        #Only add departures that have yet to happen
        if minutesUntil >= 0:
            predictions.append(minutesUntil)

    #Only returns predictions if there is data
    return predictions if predictions else None

def findWaitTimes(predictions:list):
    """
    Creates a list of wait times
    Args: Time predictions
    Returns: List of wait times
    """
    listOfWaitTimes = []
    if predictions and len(predictions) > 1:
        #Cannot index one past the index, so has to go one less
        for i in range(len(predictions)-1):
            #Finds difference between index number and next number
            listOfWaitTimes.append(abs(predictions[i]-predictions[i+1]))
        return listOfWaitTimes
    else:
        #Ensures no error when there is no data
        return None

def findMeanTime(listOfTimes:list):
    """
    Finds the mean using NumPy
    Args: List of times
    Returns: Mean value of times type int
    """
    if listOfTimes:
        meanTime = np.mean(listOfTimes)
    else:
        meanTime = 0
    return meanTime

def findMedianTime(listOfTimes):
    """
    Finds the median using NumPy
    Args: List of times
    Returns: median value of times type int
    """
    if listOfTimes:
        medianTime = np.median(listOfTimes)
    else:
        medianTime = 0
    return medianTime

def findStDevTime(listOfTimes):
    """
    Finds the standard deviation using NumPy
    Args: List of times
    Returns: Standard deviation value of times type int
    """
    if listOfTimes:
        stDevTime = np.std(listOfTimes)
    else:
        stDevTime = 0
    return stDevTime

def runthroughStations():
    """
    Main function:
    Iterates through stations to print each station's data
    """

    listofwaittimes = []
    #Using the dictionary of stops, iterates through each station ID and name
    for stopId, Name in stopDict.items():
        allPredictions = getNextDeparture(stopId, Name, directionId)

        waitTimes = findWaitTimes(allPredictions)

        meanWaitTime = findMeanTime(waitTimes)
        listofwaittimes.append(meanWaitTime)

        medianWaitTime = findMedianTime(waitTimes)

        stDevTime = findStDevTime(waitTimes)



    return listofwaittimes

def numpyStations():
    """
    Iterates through stations and directions to gather and return a DataFrame
    with mean, median, and standard deviation for each station and direction.
    """
    all_data = []
    # Iterate through both directions
    for direction in [0, 1]:
        direction_name = 'Towards Boston College (0)' if direction == 0 else 'Towards Government Center (1)'
        # Using dictionary of stops, iterates through each station
        for stopId, Name in stopDict.items():
            # Temporarily set the global directionId for getNextDeparture to use
            global directionId
            original_directionId = directionId
            directionId = direction

            allPredictions = getNextDeparture(stopId, Name, directionId)
            waitTimes = findWaitTimes(allPredictions)

            # Restore the original directionId
            directionId = original_directionId

            meanWaitTime = findMeanTime(waitTimes)
            medianWaitTime = findMedianTime(waitTimes)
            stDevTime = findStDevTime(waitTimes)

            all_data.append({
                'Station': Name,
                'Direction': direction_name,
                'Mean (in Min)': meanWaitTime,
                'Median (in Min)': medianWaitTime,
                'Standard Deviation (in Min': stDevTime
            })

    # Create a DataFrame from the collected data
    df_stats = pd.DataFrame(all_data)
    return df_stats


# The rest of the code in this cell is related to the original plot and numpyStations usage,
# which can be kept or removed depending on the user's overall goal.
# For now, I will keep it as is, but the numpyStations function is modified.


listofwaittimes = runthroughStations()
stations = [items for items in stopDict.values()]

# This part now calls the modified numpyStations which returns a DataFrame
stops_df_with_both_directions = numpyStations()

# Display the new DataFrame
display(stops_df_with_both_directions.round(2))

plt.figure(figsize=(10, 6))  # Set the size of the figure
plt.bar(stations, listofwaittimes, color='green', alpha=0.7)  # alpha controls transparency
plt.xlabel('Station', fontsize=12)
plt.ylabel('Average Wait Time (minutes)', fontsize=12)
plt.title('Average Wait Times at Green Line Stations', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')  # Rotate station names for readability
plt.tight_layout()  # Prevents labels from being cut off
plt.savefig('wait_times_bar.png')  # Save the figure
plt.show()  # Display the figure
