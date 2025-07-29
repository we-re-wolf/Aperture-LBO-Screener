"""
This module provides a high-performance connector for fetching financial
market data using the yfinance library, with built-in caching.
"""

import yfinance as yf
from typing import Dict, Any

class MarketDataConnector:
    """
    A class to interact with the yfinance API for fetching market data.
    Includes an in-memory cache to prevent redundant API calls within a single run.
    """
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get_company_info(self, ticker: str) -> Dict[str, Any] | None:
        """
        Fetches key market data for a single stock ticker.

        Args:
            ticker (str): The stock ticker.

        Returns:
            Dict[str, Any] | None: A dictionary containing key market data,
                                  or None if the ticker is invalid or data is missing.
        """
        if ticker in self.cache:
            return self.cache[ticker]

        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            if not info or info.get('marketCap') is None or info.get('enterpriseValue') is None:
                # print(f"Warning: Could not retrieve valid market data for ticker '{ticker}'.")
                self.cache[ticker] = None # Cache the failure to avoid re-querying
                return None

            required_data = {
                'ticker': info.get('symbol'),
                'companyName': info.get('shortName'),
                'marketCap': info.get('marketCap'),
                'enterpriseValue': info.get('enterpriseValue'),
                'totalDebt': info.get('totalDebt'),
                'totalCash': info.get('totalCash'),
                'ebitda': info.get('ebitda'),
                'sector': info.get('sector'),
                'industry': info.get('industry')
            }
            
            self.cache[ticker] = required_data
            return required_data

        except Exception as e:
            # print(f"Error fetching market data for {ticker}: {e}")
            self.cache[ticker] = None
            return None
