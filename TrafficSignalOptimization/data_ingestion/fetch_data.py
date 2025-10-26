"""
Data Fetching Module
Fetches traffic data from NYS Traffic Data Viewer OData Endpoint.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

# NYS Traffic Data Viewer OData Endpoint
ODATA_BASE_URL = "https://data.ny.gov/resource/qjpt-z4rb.json"
CONTINUOUS_COUNTS_URL = "https://data.ny.gov/resource/qzve-kjga.json"
SHORT_COUNTS_URL = "https://data.ny.gov/resource/qjpt-z4rb.json"


class TrafficDataFetcher:
    """Handles fetching traffic data from NYS OData endpoints."""
    
    def __init__(self, app_token: Optional[str] = None):
        """
        Initialize data fetcher.
        
        Args:
            app_token: Optional Socrata app token for higher rate limits
        """
        self.app_token = app_token
        self.session = requests.Session()
        if app_token:
            self.session.headers.update({'X-App-Token': app_token})
    
    def fetch_continuous_counts(
        self,
        county: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch continuous count data.
        
        Args:
            county: Filter by county name
            limit: Maximum number of records to fetch
            offset: Record offset for pagination
            
        Returns:
            List of traffic data records
        """
        params = {
            '$limit': limit,
            '$offset': offset,
            '$order': 'date DESC'
        }
        
        if county:
            params['$where'] = f"county='{county}'"
        
        try:
            response = self.session.get(CONTINUOUS_COUNTS_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Fetched {len(data)} continuous count records")
            return self._parse_traffic_data(data, 'continuous')
            
        except requests.RequestException as e:
            logger.error(f"Error fetching continuous counts: {e}")
            return []
    
    def fetch_short_counts(
        self,
        county: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch short count data.
        
        Args:
            county: Filter by county name
            limit: Maximum number of records to fetch
            offset: Record offset for pagination
            
        Returns:
            List of traffic data records
        """
        params = {
            '$limit': limit,
            '$offset': offset,
            '$order': 'date DESC'
        }
        
        if county:
            params['$where'] = f"county='{county}'"
        
        try:
            response = self.session.get(SHORT_COUNTS_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Fetched {len(data)} short count records")
            return self._parse_traffic_data(data, 'short')
            
        except requests.RequestException as e:
            logger.error(f"Error fetching short counts: {e}")
            return []
    
    def _parse_traffic_data(
        self, 
        raw_data: List[Dict[str, Any]], 
        data_type: str
    ) -> List[Dict[str, Any]]:
        """
        Parse raw traffic data into standardized format.
        
        Args:
            raw_data: Raw data from API
            data_type: Type of data ('continuous' or 'short')
            
        Returns:
            Parsed traffic data records
        """
        parsed_data = []
        
        for record in raw_data:
            try:
                parsed_record = {
                    'county': record.get('county', '').strip(),
                    'station_id': record.get('station_id', record.get('rc_station', '')),
                    'direction': record.get('direction', record.get('dir', 'N')),
                    'timestamp': self._parse_timestamp(record),
                    'volume': int(record.get('volume', record.get('aadt', 0))),
                    'speed': float(record.get('speed', 0)) if 'speed' in record else None,
                    'occupancy': float(record.get('occupancy', 0)) if 'occupancy' in record else None,
                    'data_type': data_type
                }
                parsed_data.append(parsed_record)
            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing record: {e}")
                continue
        
        return parsed_data
    
    def _parse_timestamp(self, record: Dict[str, Any]) -> str:
        """Parse timestamp from various formats in the data."""
        # Try different timestamp fields
        timestamp_fields = ['date', 'timestamp', 'datetime']
        
        for field in timestamp_fields:
            if field in record:
                try:
                    # Handle ISO format timestamps
                    dt = datetime.fromisoformat(record[field].replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, AttributeError):
                    pass
        
        # Default to current timestamp if parsing fails
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def fetch_all_data(
        self,
        county: str,
        max_records: int = 10000
    ) -> List[Dict[str, Any]]:
        """
        Fetch all available data for a county.
        
        Args:
            county: County name
            max_records: Maximum total records to fetch
            
        Returns:
            Combined list of all traffic data
        """
        all_data = []
        batch_size = 1000
        
        # Fetch continuous counts
        for offset in range(0, max_records, batch_size):
            continuous = self.fetch_continuous_counts(county, batch_size, offset)
            if not continuous:
                break
            all_data.extend(continuous)
            time.sleep(0.5)  # Rate limiting
        
        # Fetch short counts
        for offset in range(0, max_records, batch_size):
            short = self.fetch_short_counts(county, batch_size, offset)
            if not short:
                break
            all_data.extend(short)
            time.sleep(0.5)  # Rate limiting
        
        logger.info(f"Fetched total of {len(all_data)} records for {county}")
        return all_data


def fetch_traffic_data(
    county: Optional[str] = None,
    app_token: Optional[str] = None,
    max_records: int = 10000
) -> List[Dict[str, Any]]:
    """
    Convenience function to fetch traffic data.
    
    Args:
        county: County name to filter by
        app_token: Optional Socrata app token
        max_records: Maximum records to fetch
        
    Returns:
        List of traffic data records
    """
    fetcher = TrafficDataFetcher(app_token)
    if county:
        return fetcher.fetch_all_data(county, max_records)
    else:
        return fetcher.fetch_continuous_counts(limit=max_records)


def fetch_data_by_county(county: str, app_token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch all traffic data for a specific county.
    
    Args:
        county: County name
        app_token: Optional Socrata app token
        
    Returns:
        List of traffic data records
    """
    return fetch_traffic_data(county=county, app_token=app_token)

