"""
This module applies a set of quantitative filters to a DataFrame of company
metrics to identify potential LBO candidates.
"""

import pandas as pd
from typing import Dict, Any

class Screener:
    """
    Filters a list of companies based on predefined LBO criteria.
    """
    def __init__(self, metrics_df: pd.DataFrame, criteria: Dict[str, Any]):
        self.metrics_df = metrics_df
        self.criteria = criteria
        self.pass_fail_log = []

    def run_screen(self) -> pd.DataFrame:
        """
        Applies all screening criteria to the metrics DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing only the companies that
                          passed all screening criteria.
        """
        print("\n--- Running LBO Candidate Screen ---")
        
        screened_df = self.metrics_df.copy()
        
        
        # Size Filter
        screened_df = self._apply_filter(screened_df, 'LTM EBITDA', 
                                         lambda x: x >= self.criteria['MIN_LTM_EBITDA_USD'])
        
        # Valuation Filter
        screened_df = self._apply_filter(screened_df, 'EV/EBITDA', 
                                         lambda x: x <= self.criteria['MAX_EV_EBITDA_MULTIPLE'])
        
        # Leverage Filter
        screened_df = self._apply_filter(screened_df, 'Net Debt/EBITDA', 
                                         lambda x: x <= self.criteria['MAX_NET_DEBT_EBITDA'])
        
        # Growth Filter
        screened_df = self._apply_filter(screened_df, 'Revenue CAGR', 
                                         lambda x: x >= self.criteria['MIN_REVENUE_CAGR_5Y'])
        
        # Stability Filter
        screened_df = self._apply_filter(screened_df, 'EBITDA Margin Std Dev', 
                                         lambda x: x <= self.criteria['MAX_EBITDA_MARGIN_STD_DEV'])
        
        # Capital Intensity Filter
        screened_df = self._apply_filter(screened_df, 'CapEx as % of Sales', 
                                         lambda x: x <= self.criteria['MAX_CAPEX_AS_PERCENT_OF_SALES'])

        print(f"\nScreening complete. Found {len(screened_df)} potential LBO candidates.")
        return screened_df

    def _apply_filter(self, df: pd.DataFrame, column: str, condition) -> pd.DataFrame:
        """
        Helper function to apply a single filter and log the results.
        """
        initial_count = len(df)
        filtered_df = df.dropna(subset=[column]).loc[condition(df[column])]
        final_count = len(filtered_df)
        
        print(f"  - Filtering by '{column}': {initial_count} -> {final_count} companies passed.")
        return filtered_df

