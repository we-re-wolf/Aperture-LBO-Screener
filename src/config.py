# src/config.py

"""
Configuration file for the Aperture LBO Screening Platform.

This file stores API keys, screening criteria, and model assumptions
to allow for easy adjustments and calibration.
"""

# --- API Keys ---
# It's recommended to use environment variables in a real production environment
SEC_API_KEY = "YOUR_SEC_API_KEY"

# --- Screening Universe ---
# Path to the CSV file containing the list of tickers to screen
UNIVERSE_FILE_PATH = "data/universe/russell_3000_tickers.csv"

# --- Quantitative LBO Screening Criteria ---
# These values define what makes a good LBO candidate.
SCREENING_CRITERIA = {
    # Financial Stability & Performance
    'MIN_REVENUE_CAGR_5Y': 0.03,  # Minimum 5-year revenue CAGR of 3%
    'MAX_EBITDA_MARGIN_STD_DEV': 0.15, # Max 15% standard deviation in historical EBITDA margin

    # Capital Intensity
    'MAX_CAPEX_AS_PERCENT_OF_SALES': 0.05, # CapEx should be below 5% of sales on average

    # Valuation
    'MAX_EV_EBITDA_MULTIPLE': 12.0, # Entry multiple should be less than 12.0x

    # Debt Capacity
    'MAX_NET_DEBT_EBITDA': 2.0, # Existing leverage should be less than 2.0x

    # Size & Maturity
    'MIN_LTM_EBITDA_USD': 50_000_000 # LTM EBITDA must be at least $50 million
}

# --- LBO Model Assumptions ---
LBO_ASSUMPTIONS = {
    'PROJECTION_YEARS': 5,
    'ENTRY_LEVERAGE_MULTIPLE': 6.0, # Total debt taken on is 6.0x LTM EBITDA
    'EXIT_MULTIPLE_PREMIUM': 0.0, # Assume exit multiple is the same as entry multiple
    'INTEREST_RATE': 0.07, # Assumed average interest rate on debt
    'TAX_RATE': 0.25 # Assumed corporate tax rate
}
