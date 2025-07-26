import os
import requests

API_KEY = os.getenv("My_511Ny_API_key")
BASE_URL = "https://api.511ny.org/Traffic/Incidents"

def fetch_incidents(county: str):
    params = {
        "format": "json",
        "county": county,
        "key": API_KEY
    }
    resp = requests.get(BASE_URL, params=params)
    resp.raise_for_status()
    return resp.json()