"""
Data Ingestion Module
Handles fetching traffic data from NYS Traffic Data Viewer OData Endpoint
and storing it in a local SQLite database.
"""

from .fetch_data import fetch_traffic_data, fetch_data_by_county
from .database import DatabaseManager

__all__ = ['fetch_traffic_data', 'fetch_data_by_county', 'DatabaseManager']

