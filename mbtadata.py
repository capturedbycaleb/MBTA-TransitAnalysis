import requests
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # for visualizations

# --- Configuration ---
apiKey = "68b143c7928743bfbf721868967a0a2c"
routeId = "Green-B"
directionId = DIRECTION_ID=0 # 1 means headed toward Gov Center, 0 means headed toward Boston College

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

def getNextarrival(stopId:str, name:str, direction):
    """
    Appends station name and time until next arrival to a list

    Arugments:
      - stopId: station id
      - name: station name
      - direction: direction of line
    Returns: List of minutes until next arrivals
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

    #Iterate through each set of attributes(each one contains a arrival time)
    #Data structure: /data/{index}/attributes/arrival_time
    for i in range(len(numerates)):
        attributes = numerates[i].get("attributes")
        arrivalIso = attributes.get("arrival_time")

        #Ensures no error when there is no data
        if not arrivalIso:
            continue

        #Clean up arrival time as it is returned in ISO
        isoNoColon = arrivalIso[:-3] + arrivalIso[-2:]
        arrivalTime = datetime.datetime.strptime(
            isoNoColon,
            "%Y-%m-%dT%H:%M:%S%z"
        )

        #Use datetime.now to find current time
        now = datetime.datetime.now(arrivalTime.tzinfo)

        #Calculate time until next arrival
        timeUntilarrival = arrivalTime - now

        #Convert to minutes
        minutesUntil = int(timeUntilarrival.total_seconds() / 60)

        #Only add arrivals that have yet to happen
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
        allPredictions = getNextarrival(stopId, Name, directionId)

        waitTimes = findWaitTimes(allPredictions)

        meanWaitTime = findMeanTime(waitTimes)
        listofwaittimes.append(meanWaitTime)

        medianWaitTime = findMedianTime(waitTimes)

        stDevTime = findStDevTime(waitTimes)


    return listofwaittimes
        #Print data
       # if waitTimes is not None and len(waitTimes) > 0:
       #     print(f"{Name} Mean wait time: {meanWaitTime:.2f} Minutes, Median wait time: {medianWaitTime:.2f} Minutes, Standard Deviation: {stDevTime:.2f}")
       #     print("---------------------------------------------------------------------------------------------------------")
       # else:
       #     print(f"No valid wait time data (fewer than 2 predictions) for {Name}.")
       #     print("---------------------------------------------------------------------------------------------------------")

listofwaittimes = runthroughStations()
stations = [items for items in stopDict.values()]

plt.figure(figsize=(10, 6))  # Set the size of the figure
plt.bar(stations, listofwaittimes, color='green', alpha=0.7)  # alpha controls transparency
plt.xlabel('Station', fontsize=12)
plt.ylabel('Average Wait Time (minutes)', fontsize=12)
plt.title('Average Wait Times at Green Line Stations', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')  # Rotate station names for readability
plt.tight_layout()  # Prevents labels from being cut off
plt.savefig('wait_times_bar.png')  # Save the figure
plt.show()  # Display the figure