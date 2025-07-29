"""
This module contains the core logic for running a simplified, automated
Leveraged Buyout (LBO) model for a given company.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

class LBOModel:
    """
    Performs a high-level LBO analysis on a single company, including
    sensitivity analysis on key assumptions.
    """
    def __init__(self, candidate_data: pd.Series, assumptions: Dict):
        self.data = candidate_data
        self.assumptions = assumptions
        self.projections = None # To store projections once calculated

    def run_model(self, entry_multiple_override=None, exit_multiple_override=None) -> Dict[str, Any] | None:
        """
        Executes the full LBO model from entry to exit.
        Allows for overriding key assumptions for sensitivity analysis.
        """
        ltm_ebitda = self.data.get('LTM EBITDA')
        base_entry_multiple = self.data.get('EV/EBITDA')
        
        entry_multiple = entry_multiple_override if entry_multiple_override is not None else base_entry_multiple
        
        if pd.isna(ltm_ebitda) or pd.isna(entry_multiple):
            return None

        entry_enterprise_value = ltm_ebitda * entry_multiple
        entry_debt = ltm_ebitda * self.assumptions['ENTRY_LEVERAGE_MULTIPLE']
        entry_equity = entry_enterprise_value - entry_debt
        
        if entry_equity <= 0:
            return None

        if self.projections is None:
            revenue_cagr = self.data.get('Revenue CAGR', 0.03)
            capex_percent_sales = self.data.get('CapEx as % of Sales', 0.03)
            self.projections = self._project_cash_flows(ltm_ebitda, revenue_cagr, capex_percent_sales)

        debt_schedule = self._model_debt_schedule(entry_debt, self.projections['Unlevered FCF'])
        final_debt_balance = debt_schedule.iloc[-1]['Ending Debt']

        exit_ebitda = self.projections.iloc[-1]['EBITDA']
        exit_multiple = exit_multiple_override if exit_multiple_override is not None else (entry_multiple + self.assumptions['EXIT_MULTIPLE_PREMIUM'])
        
        exit_enterprise_value = exit_ebitda * exit_multiple
        exit_equity_value = exit_enterprise_value - final_debt_balance

        moic = exit_equity_value / entry_equity
        years = self.assumptions['PROJECTION_YEARS']
        irr = (moic ** (1 / years)) - 1 if moic > 0 else -1.0

        return {
            'Ticker': self.data.name, 'Entry EV': entry_enterprise_value,
            'Entry Equity': entry_equity, 'Exit EV': exit_enterprise_value,
            'Exit Equity': exit_equity_value, 'IRR': irr, 'MOIC': moic
        }

    def run_sensitivity_analysis(self) -> Tuple[pd.DataFrame, pd.DataFrame] | None:
        """
        Runs the LBO model across a range of entry and exit multiples.
        
        Returns:
            A tuple containing two DataFrames: one for IRR and one for MOIC sensitivity.
        """
        base_entry_multiple = self.data.get('EV/EBITDA')
        if pd.isna(base_entry_multiple):
            return None, None

        entry_multiples = np.arange(base_entry_multiple - 1.0, base_entry_multiple + 1.1, 0.5)
        exit_multiples = np.arange(base_entry_multiple - 1.0, base_entry_multiple + 1.1, 0.5)

        irr_results = pd.DataFrame(index=entry_multiples, columns=exit_multiples)
        moic_results = pd.DataFrame(index=entry_multiples, columns=exit_multiples)

        for entry_mult in entry_multiples:
            for exit_mult in exit_multiples:
                result = self.run_model(entry_multiple_override=entry_mult, exit_multiple_override=exit_mult)
                if result:
                    irr_results.loc[entry_mult, exit_mult] = result['IRR']
                    moic_results.loc[entry_mult, exit_mult] = result['MOIC']
        
        irr_results.index.name = "Entry Multiple"
        irr_results.columns.name = "Exit Multiple"
        moic_results.index.name = "Entry Multiple"
        moic_results.columns.name = "Exit Multiple"
        
        return irr_results.astype(float), moic_results.astype(float)

    def _project_cash_flows(self, ltm_ebitda, revenue_cagr, capex_percent_sales) -> pd.DataFrame:
        """Projects EBITDA and calculates Unlevered Free Cash Flow."""
        projections = pd.DataFrame(index=[f'Year {i+1}' for i in range(self.assumptions['PROJECTION_YEARS'])])
        projected_ebitda = [ltm_ebitda * (1 + revenue_cagr) ** (i+1) for i in range(len(projections))]
        projections['EBITDA'] = projected_ebitda
        
        tax_rate = self.assumptions['TAX_RATE']
        d_and_a = projections['EBITDA'] * 0.15 
        ebit = projections['EBITDA'] - d_and_a
        taxes = ebit * tax_rate
        nopat = ebit - taxes
        change_in_nwc = projections['EBITDA'].diff().fillna(0) * 0.05
        capex = projections['EBITDA'] * capex_percent_sales
        projections['Unlevered FCF'] = nopat + d_and_a - capex - change_in_nwc
        return projections

    def _model_debt_schedule(self, starting_debt, fcf_series) -> pd.DataFrame:
        """Models the annual paydown of debt using a cash flow sweep."""
        schedule = pd.DataFrame(index=fcf_series.index)
        debt_balance = starting_debt
        balances = []
        for year, fcf in fcf_series.items():
            interest_payment = debt_balance * self.assumptions['INTEREST_RATE']
            cash_available_for_debt = fcf - interest_payment
            principal_paydown = min(debt_balance, max(0, cash_available_for_debt))
            debt_balance -= principal_paydown
            balances.append(debt_balance)
        schedule['Ending Debt'] = balances
        return schedule
