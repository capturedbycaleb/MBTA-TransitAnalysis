# config.py
import os
from dotenv import load_dotenv


# --- Configuration ---
# Your API Key (ensure this is handled securely)
API_KEY = os.getenv("MBTA_API_KEY")
# MBTA Green Line B-branch
ROUTE_ID = "Green-B"
# 1: toward Gov Center, 0: toward Boston College (Inbound/Outbound)
DIRECTION_ID = 0
# Base URL for the MBTA V3 API predictions endpoint
API_URL = "https://api-v3.mbta.com/predictions"

# Dictionary of each stop's ID and name (Green-B stops)
STOP_DICT = {
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