import requests
import pandas as pd
from datetime import datetime, date
from typing import Optional, Union, List, Dict
from dateutil.parser import parse
from urllib.parse import urljoin, urlparse, parse_qs
from .config import Config

class EODHDOptions:
    """
    A client for the EODHD Options API.
    """
    
    BASE_URL = "https://eodhd.com/api/mp/unicornbay/options/eod"
    DEFAULT_PAGE_SIZE = 1000
    MAX_OFFSET = 10000  # API limit for offset
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the EODHD Options client.
        
        Args:
            api_key (Optional[str]): Your EODHD API key. If not provided, will attempt to load from config.
        """
        self.config = Config()
        
        if api_key:
            self.api_key = api_key
            # Save the provided key for future use
            self.config.save_api_key(api_key)
        else:
            # Try to load from config
            self.api_key = self.config.get_api_key()
            if not self.api_key:
                raise ValueError(
                    "No API key provided and none found in config. "
                    "Please provide an API key or use save_api_key() to store one."
                )
        
        self.session = requests.Session()
    
    @classmethod
    def save_api_key(cls, api_key: str):
        """
        Save an API key for future use.
        
        Args:
            api_key (str): The API key to save
        """
        config = Config()
        config.save_api_key(api_key)
    
    def _make_request(self, params: Dict = None) -> Dict:
        """
        Make a request to the EODHD API.
        
        Args:
            params (Dict, optional): Query parameters
            
        Returns:
            Dict: API response
        """
        if params is None:
            params = {}
        
        params['api_token'] = self.api_key
        
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def _get_next_page_params(self, next_url: str) -> Dict:
        """
        Extract pagination parameters from the next page URL.
        
        Args:
            next_url (str): The URL for the next page
            
        Returns:
            Dict: Parameters for the next page request
        """
        parsed = urlparse(next_url)
        params = parse_qs(parsed.query)
        
        # Convert list values to single values
        return {k: v[0] for k, v in params.items() if k != 'api_token'}
    
    def _validate_date(self, date_val: Union[str, datetime, date]) -> str:
        """
        Validate and format a date.
        
        Args:
            date_val (Union[str, datetime, date]): Date to validate
            
        Returns:
            str: Formatted date string (YYYY-MM-DD)
        """
        if isinstance(date_val, str):
            date_val = parse(date_val)
        if isinstance(date_val, datetime):
            date_val = date_val.date()
        return date_val.strftime("%Y-%m-%d")
    
    def get_options(
        self,
        ticker: str,
        from_date: Optional[Union[str, datetime, date]] = None,
        to_date: Optional[Union[str, datetime, date]] = None,
        min_strike: Optional[float] = None,
        max_strike: Optional[float] = None,
        option_type: Optional[str] = None,
        sort: str = "exp_date",
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get options data for a specific ticker with filters.
        
        Args:
            ticker (str): Ticker symbol
            from_date (Union[str, datetime, date], optional): Start date for expiration range
            to_date (Union[str, datetime, date], optional): End date for expiration range
            min_strike (float, optional): Minimum strike price
            max_strike (float, optional): Maximum strike price
            option_type (str, optional): Type of options to fetch ('call', 'put', or None)
            sort (str, optional): Field to sort by. Defaults to 'exp_date'
            limit (int, optional): Maximum number of results to return. If None, fetches up to MAX_OFFSET results
            
        Returns:
            pd.DataFrame: Options data
        """
        base_params = {
            'filter[underlying_symbol]': ticker,
            'sort': sort,
            'page[limit]': self.DEFAULT_PAGE_SIZE
        }
        
        if from_date:
            base_params['filter[exp_date_from]'] = self._validate_date(from_date)
        if to_date:
            base_params['filter[exp_date_to]'] = self._validate_date(to_date)
        if min_strike:
            base_params['filter[strike_from]'] = min_strike
        if max_strike:
            base_params['filter[strike_to]'] = max_strike
        if option_type:
            base_params['filter[type]'] = option_type.lower()
        
        all_data = []
        total_fetched = 0
        current_offset = 0
        
        while current_offset <= self.MAX_OFFSET:
            params = base_params.copy()
            params['page[offset]'] = current_offset
            
            data = self._make_request(params)
            
            if not isinstance(data, dict) or 'data' not in data:
                break
                
            # Extract attributes from the data
            batch_data = []
            for item in data['data']:
                if 'attributes' in item:
                    batch_data.append(item['attributes'])
            
            if not batch_data:  # No more data
                break
                
            all_data.extend(batch_data)
            total_fetched += len(batch_data)
            
            # Check if we've hit the user's limit
            if limit and total_fetched >= limit:
                all_data = all_data[:limit]
                break
            
            # If we got less than the page size, we've reached the end
            if len(batch_data) < self.DEFAULT_PAGE_SIZE:
                break
                
            current_offset += self.DEFAULT_PAGE_SIZE
            
            # Print progress
            print(f"Fetched {total_fetched:,} options...", end='\r')
        
        print()  # New line after progress updates
        return pd.DataFrame(all_data)
    
    def get_options_chain(self, ticker: str) -> pd.DataFrame:
        """
        Get the current options chain for a ticker.
        
        Args:
            ticker (str): Ticker symbol
            
        Returns:
            pd.DataFrame: Options chain data
        """
        params = {'symbol': ticker}
        data = self._make_request('chain', params)
        if isinstance(data, dict) and 'data' in data:
            return pd.DataFrame(data['data'])
        return pd.DataFrame(data)
    
    def get_contract_details(
        self,
        ticker: str,
        expiration_date: Union[str, datetime],
        strike: float,
        option_type: str
    ) -> Dict:
        """
        Get details for a specific options contract.
        
        Args:
            ticker (str): Ticker symbol
            expiration_date (Union[str, datetime]): Contract expiration date
            strike (float): Strike price
            option_type (str): Option type ('call' or 'put')
            
        Returns:
            Dict: Contract details
        """
        params = {
            'symbol': ticker,
            'expiration': self._validate_date(expiration_date),
            'strike': strike,
            'type': option_type.upper()
        }
        return self._make_request('details', params)
    
    def get_current_price(self, ticker: str) -> float:
        """
        Get the current price of the underlying asset.
        
        Args:
            ticker (str): Ticker symbol
            
        Returns:
            float: Current price
        """
        url = "https://eodhd.com/api/real-time/{}".format(ticker)
        params = {'api_token': self.api_key, 'fmt': 'json'}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return float(data['close']) 