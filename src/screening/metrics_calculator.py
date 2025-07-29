"""
This module calculates all the quantitative metrics required for the LBO
screening process, using both market data and historical financial statements.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class MetricsCalculator:
    """
    Calculates a suite of financial metrics for a single company with robust
    fallbacks for incomplete historical data.
    """
    def __init__(self, ticker: str, market_data: Dict, sec_data: Dict[str, pd.DataFrame]):
        self.ticker = ticker
        self.market_data = market_data
        self.sec_data = sec_data
        
        self.concept_map = {
            'Revenue': ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'TotalRevenues', 'SalesRevenueNet'],
            'OperatingIncome': ['OperatingIncomeLoss'],
            'DepreciationAndAmortization': ['DepreciationAndAmortization', 'DepreciationDepletionAndAmortization'],
            'CapEx': [
                'CapitalExpenditures', 
                'PurchaseOfPropertyAndEquipmentNet', 
                'PaymentsToAcquirePropertyPlantAndEquipment'
            ]
        }

    def _get_financial_series(self, statement_key: str, concept: str) -> pd.Series | None:
        """Safely retrieves a full time series for a financial concept."""
        statement_df = self.sec_data.get(statement_key)
        if statement_df is None or statement_df.empty:
            return None
        
        for tag in self.concept_map.get(concept, []):
            if tag in statement_df.index:
                series = statement_df.loc[tag]
                numeric_series = pd.to_numeric(series, errors='coerce').dropna()
                return numeric_series if not numeric_series.empty else None
        return None

    def calculate_all_metrics(self) -> Dict[str, Any] | None:
        """
        Calculates all screening metrics and returns them in a dictionary.
        """
        operating_income = self._get_financial_series('Income Statement', 'OperatingIncome')
        d_and_a = self._get_financial_series('Cash Flow', 'DepreciationAndAmortization')
        
        ebitda_series = None
        if operating_income is not None and d_and_a is not None:
            ebitda_series = operating_income.add(d_and_a, fill_value=0)
        
        ltm_ebitda = ebitda_series.iloc[0] if ebitda_series is not None and not ebitda_series.empty else self.market_data.get('ebitda')

        if ltm_ebitda is None or ltm_ebitda <= 0:
            return None

        revenue_series = self._get_financial_series('Income Statement', 'Revenue')
        cagr = None
        if revenue_series is not None and len(revenue_series) > 1:
            for years in [4, 2, 1]:
                if len(revenue_series) > years:
                    start_value = revenue_series.iloc[years]
                    end_value = revenue_series.iloc[0]
                    if start_value > 0:
                        cagr = (end_value / start_value) ** (1/years) - 1
                        break
        
        ebitda_margin_std = None
        if revenue_series is not None and ebitda_series is not None:
            aligned_revenue, aligned_ebitda = revenue_series.align(ebitda_series, join='inner')
            if not aligned_ebitda.empty:
                ebitda_margin_series = aligned_ebitda / aligned_revenue
                if len(ebitda_margin_series) > 1:
                    ebitda_margin_std = ebitda_margin_series.std()

        capex_series = self._get_financial_series('Cash Flow', 'CapEx')
        capex_as_percent_of_sales = None
        if capex_series is not None and revenue_series is not None:
            for years in [3, 2, 1]:
                if len(capex_series) >= years and len(revenue_series) >= years:
                    capex_sum = abs(capex_series.iloc[:years].sum())
                    revenue_sum = revenue_series.iloc[:years].sum()
                    if revenue_sum > 0:
                        capex_as_percent_of_sales = capex_sum / revenue_sum
                        break

        net_debt = self.market_data.get('totalDebt', 0) - self.market_data.get('totalCash', 0)
        net_debt_ebitda = net_debt / ltm_ebitda if ltm_ebitda else None
        ev_ebitda = self.market_data.get('enterpriseValue') / ltm_ebitda if ltm_ebitda else None

        return {
            'Ticker': self.ticker,
            'Company Name': self.market_data.get('companyName'),
            'Sector': self.market_data.get('sector'),
            'LTM EBITDA': ltm_ebitda,
            'EV/EBITDA': ev_ebitda,
            'Net Debt/EBITDA': net_debt_ebitda,
            'Revenue CAGR': cagr,
            'EBITDA Margin Std Dev': ebitda_margin_std,
            'CapEx as % of Sales': capex_as_percent_of_sales
        }
