from typing import List, Dict
import pandas as pd

def clean_incidents(data: Dict) -> pd.DataFrame:
    features = data.get("features", [])
    rows = [{
        "id": feat.get("id"),
        "type": feat["properties"].get("EventType"),
        "description": feat["properties"].get("Description"),
        "start": feat["properties"].get("StartTime"),
        "end": feat["properties"].get("EndTime"),
        "latitude": feat["geometry"]["coordinates"][1],
        "longitude": feat["geometry"]["coordinates"][0]
    } for feat in features]
    df = pd.DataFrame(rows)
    df["start"] = pd.to_datetime(df["start"], error="coerce")
    df["end"] = pd.to_datetime(df["end"], error = "coerce")
    return df