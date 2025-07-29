"""
This module provides a high-performance connector for sourcing and parsing
multi-year financial statements from SEC EDGAR filings.
"""

import pandas as pd
from typing import Dict, Any, Tuple

from sec_api import QueryApi, XbrlApi
from src.config import SEC_API_KEY

class SecDataConnector:
    """
    Sources and parses 10-K filings into structured pandas DataFrames.
    Includes an in-memory cache and robust error handling.
    """
    def __init__(self):
        if not SEC_API_KEY or SEC_API_KEY == "PASTE_YOUR_SEC_API_KEY_HERE":
            raise ValueError("SEC_API_KEY is not set in config.py. Please get a free key from sec-api.io.")
        self.query_api = QueryApi(api_key=SEC_API_KEY)
        self.xbrl_api = XbrlApi(api_key=SEC_API_KEY)
        self.cache: Dict[str, Dict[str, pd.DataFrame]] = {}

    def _parse_statement(self, xbrl_json: Dict[str, Any], statement_key: str) -> pd.DataFrame:
        """
        Parses a single financial statement from XBRL JSON into a clean DataFrame.
        """
        if statement_key not in xbrl_json:
            return pd.DataFrame()

        statement_data = {}
        for concept, facts in xbrl_json[statement_key].items():
            if not isinstance(facts, list):
                continue

            for fact in facts:
                if not isinstance(fact, dict):
                    continue

                if 'segment' not in fact and 'value' in fact:
                    period_obj = fact.get('period')
                    period_date = None

                    if isinstance(period_obj, dict):
                        period_date = period_obj.get('endDate') or period_obj.get('instant')
                    elif isinstance(period_obj, str):
                        period_date = period_obj
                    
                    if period_date:
                        if period_date not in statement_data:
                            statement_data[period_date] = {}
                        statement_data[period_date][concept] = pd.to_numeric(fact['value'], errors='coerce')

        if not statement_data:
            return pd.DataFrame()

        df = pd.DataFrame(statement_data)
        df.columns = pd.to_datetime(df.columns)
        df = df.reindex(sorted(df.columns, reverse=True), axis=1)
        return df

    def get_financial_statements(self, ticker: str) -> Dict[str, pd.DataFrame] | None:
        """
        Fetches and parses the latest 10-K filing for a given ticker.
        """
        if ticker in self.cache:
            return self.cache[ticker]

        print(f"  -> Sourcing SEC data for {ticker}...")
        try:
            query = {
                "query": {"query_string": {"query": f"ticker:{ticker} AND formType:\"10-K\""}},
                "from": "0", "size": "1", "sort": [{"filedAt": {"order": "desc"}}]
            }
            filings = self.query_api.get_filings(query)
            if not filings['filings']:
                print(f"     - Warning: No 10-K filings found for {ticker}.")
                self.cache[ticker] = None
                return None
            
            filing_url = filings['filings'][0]['linkToFilingDetails']
            xbrl_json = self.xbrl_api.xbrl_to_json(htm_url=filing_url)

            income_statement = self._parse_statement(xbrl_json, 'StatementsOfIncome')
            balance_sheet = self._parse_statement(xbrl_json, 'BalanceSheets')
            cash_flow = self._parse_statement(xbrl_json, 'StatementsOfCashFlows')
            
            if income_statement.empty or balance_sheet.empty or cash_flow.empty:
                 print(f"     - Warning: Could not parse one or more financial statements for {ticker}.")
                 self.cache[ticker] = None
                 return None

            parsed_statements = {
                'Income Statement': income_statement,
                'Balance Sheet': balance_sheet,
                'Cash Flow': cash_flow
            }
            self.cache[ticker] = parsed_statements
            return parsed_statements

        except Exception as e:
            print(f"     - Error processing SEC data for {ticker}: {e}")
            self.cache[ticker] = None
            return None
