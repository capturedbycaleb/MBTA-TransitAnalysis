# mbta_api.py
import requests
import datetime
from typing import List, Optional

def get_next_arrivals(stop_id: str, route_id: str, direction_id: int, api_key: str, api_url: str) -> Optional[List[int]]:
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
    headers = {"X-API-Key": api_key} if api_key else {}

    try:
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request error for stop {stop_id}: {e}")
        return None

    predictions = []

    if not data or "data" not in data or not data["data"]:
        return None

    for prediction in data["data"]:
        attributes = prediction.get("attributes")
        arrival_iso = attributes.get("arrival_time")

        if not arrival_iso:
            continue

        try:
            # Clean up ISO format and parse with timezone
            iso_no_colon = arrival_iso[:-3] + arrival_iso[-2:]
            arrival_time = datetime.datetime.strptime(iso_no_colon, "%Y-%m-%dT%H:%M:%S%z")
            now = datetime.datetime.now(arrival_time.tzinfo)

            time_until_arrival = arrival_time - now
            minutes_until = int(time_until_arrival.total_seconds() / 60)

            if minutes_until >= 0:
                predictions.append(minutes_until)
        except ValueError as e:
            print(f"Error parsing date/time for stop {stop_id}: {e}")
            continue

    return predictions if predictions else None