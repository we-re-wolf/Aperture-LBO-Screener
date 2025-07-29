# app.py

import streamlit as st
import pandas as pd
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import plotly.express as px
import plotly.graph_objects as go

# --- Add src directory to path for imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.config import UNIVERSE_FILE_PATH, SCREENING_CRITERIA, LBO_ASSUMPTIONS
from src.connectors.market_data import MarketDataConnector
from src.connectors.sec_data import SecDataConnector
from src.screening.metrics_calculator import MetricsCalculator
from src.screening.screener import Screener
from src.modeling.lbo_model import LBOModel

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Aperture | LBO Screening Platform", page_icon="🎯", layout="wide")

# --- Caching Functions for Performance ---
@st.cache_data
def run_full_pipeline():
    """
    Runs the entire data gathering, screening, and modeling pipeline.
    Returns the calculated metrics and the raw financial statements.
    """
    try:
        universe_df = pd.read_csv(UNIVERSE_FILE_PATH)
        tickers_to_screen = universe_df['Ticker'].tolist()
    except FileNotFoundError:
        st.error(f"Error: Universe file not found at '{UNIVERSE_FILE_PATH}'.")
        return None, None
    
    market_connector = MarketDataConnector()
    sec_connector = SecDataConnector()
    all_metrics, financial_statements_dict = [], {}
    progress_bar = st.progress(0, text="Fetching data and calculating metrics...")

    def process_ticker(ticker):
        market_data = market_connector.get_company_info(ticker)
        if not market_data: return None, None
        sec_data = sec_connector.get_financial_statements(ticker)
        if not sec_data: return None, None
        metrics_calculator = MetricsCalculator(ticker, market_data, sec_data)
        return metrics_calculator.calculate_all_metrics(), sec_data

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(process_ticker, ticker): ticker for ticker in tickers_to_screen}
        total_futures = len(future_to_ticker)
        for i, future in enumerate(as_completed(future_to_ticker)):
            metrics, sec_data = future.result()
            if metrics and sec_data:
                all_metrics.append(metrics)
                financial_statements_dict[metrics['Ticker']] = sec_data
            progress_bar.progress((i + 1) / total_futures)

    progress_bar.empty()
    if not all_metrics: return pd.DataFrame(), {}
    return pd.DataFrame(all_metrics).set_index('Ticker'), financial_statements_dict

# --- Sidebar for Interactive Controls ---
st.sidebar.header("🎯 Screening Control Panel")
if 'criteria' not in st.session_state: st.session_state.criteria = SCREENING_CRITERIA.copy()
st.session_state.criteria['MAX_EV_EBITDA_MULTIPLE'] = st.sidebar.slider("Max EV/EBITDA Multiple", 5.0, 25.0, st.session_state.criteria['MAX_EV_EBITDA_MULTIPLE'], 0.5)
st.session_state.criteria['MAX_NET_DEBT_EBITDA'] = st.sidebar.slider("Max Net Debt/EBITDA", 0.0, 5.0, st.session_state.criteria['MAX_NET_DEBT_EBITDA'], 0.1)
st.session_state.criteria['MIN_REVENUE_CAGR_5Y'] = st.sidebar.slider("Min Revenue CAGR (%)", 0.0, 30.0, st.session_state.criteria['MIN_REVENUE_CAGR_5Y'] * 100, 1.0) / 100.0
st.session_state.criteria['MAX_CAPEX_AS_PERCENT_OF_SALES'] = st.sidebar.slider("Max CapEx as % of Sales", 0.0, 20.0, st.session_state.criteria['MAX_CAPEX_AS_PERCENT_OF_SALES'] * 100, 0.5) / 100.0
st.session_state.criteria['MIN_LTM_EBITDA_USD'] = st.sidebar.number_input("Min LTM EBITDA ($M)", value=int(st.session_state.criteria['MIN_LTM_EBITDA_USD'] / 1_000_000)) * 1_000_000

# --- Main Application UI ---
st.title("🎯 Aperture: LBO Candidate Screening Platform")
st.markdown("Use the **Control Panel** on the left to adjust screening criteria in real-time.")

if 'metrics_df' not in st.session_state:
    st.session_state.metrics_df = None
    st.session_state.financial_statements = None

if st.button("▶️ Start / Refresh Data Pipeline"):
    metrics_df, financial_statements = run_full_pipeline()
    st.session_state.metrics_df = metrics_df
    st.session_state.financial_statements = financial_statements

if st.session_state.metrics_df is not None:
    metrics_df = st.session_state.metrics_df
    financial_statements_dict = st.session_state.financial_statements
    
    lbo_screener = Screener(metrics_df, st.session_state.criteria)
    lbo_candidates_df = lbo_screener.run_screen()

    lbo_results, sensitivity_results = [], {}
    if not lbo_candidates_df.empty:
        for ticker, candidate_data in lbo_candidates_df.iterrows():
            model = LBOModel(candidate_data, LBO_ASSUMPTIONS)
            result = model.run_model()
            if result:
                lbo_results.append(result)
                irr_table, moic_table = model.run_sensitivity_analysis()
                sensitivity_results[ticker] = {'IRR': irr_table, 'MOIC': moic_table}
    
    lbo_results_df = pd.DataFrame(lbo_results).set_index('Ticker') if lbo_results else pd.DataFrame()

    st.header("📈 LBO Candidate Shortlist")
    if lbo_results_df.empty:
        st.warning("No companies passed the current screening criteria.")
    else:
        display_df = lbo_results_df.join(lbo_candidates_df, how="inner").sort_values(by="IRR", ascending=False)
        display_df_formatted = display_df.copy()
        display_df_formatted['IRR'] = display_df_formatted['IRR'].map('{:.1%}'.format)
        display_df_formatted['MOIC'] = display_df_formatted['MOIC'].map('{:.2f}x'.format)
        st.dataframe(display_df_formatted[['Company Name', 'Sector', 'EV/EBITDA', 'Net Debt/EBITDA', 'Revenue CAGR', 'IRR', 'MOIC']])

        st.markdown("---")
        st.header("📊 Investment Memo Tear Sheet")
        selected_ticker = st.selectbox("Select a candidate to analyze:", options=display_df.index)

        if selected_ticker:
            candidate_data = display_df.loc[selected_ticker]
            
            st.subheader(f"{candidate_data['Company Name']} ({selected_ticker})")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Projected IRR", f"{candidate_data['IRR']:.1%}")
            col2.metric("Projected MOIC", f"{candidate_data['MOIC']:.2f}x")
            col3.metric("Entry EV/EBITDA", f"{candidate_data['EV/EBITDA']:.2f}x")
            col4.metric("Entry Net Leverage", f"{candidate_data['Net Debt/EBITDA']:.2f}x")

            st.subheader("LBO Transaction Structure (Sources & Uses)")
            col1, col2 = st.columns(2)
            with col1:
                entry_debt = candidate_data['Entry EV'] - candidate_data['Entry Equity']
                sources_data = {'Source': ['New Debt', 'Sponsor Equity'], 'Amount': [entry_debt, candidate_data['Entry Equity']]}
                sources_df = pd.DataFrame(sources_data)
                fig = px.pie(sources_df, values='Amount', names='Source', title='<b>Sources of Funds</b>', color_discrete_sequence=px.colors.sequential.Blues_r)
                fig.update_traces(textinfo='percent+label', insidetextorientation='radial', hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.2s}<extra></extra>")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                uses_data = {'Use': ['Purchase of Company', 'Fees & Expenses (Assumed)'], 'Amount': [candidate_data['Entry EV'] * 0.98, candidate_data['Entry EV'] * 0.02]}
                uses_df = pd.DataFrame(uses_data)
                fig = px.pie(uses_df, values='Amount', names='Use', title='<b>Uses of Funds</b>', color_discrete_sequence=px.colors.sequential.Greens_r)
                fig.update_traces(textinfo='percent+label', insidetextorientation='radial', hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.2s}<extra></extra>")
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("LBO Value Creation Bridge")
            lbo_summary_data = {
                'Component': ['Entry Equity', 'Entry Debt', 'Exit Equity', 'Debt Paydown'],
                'Value': [
                    candidate_data['Entry Equity'],
                    candidate_data['Entry EV'] - candidate_data['Entry Equity'],
                    candidate_data['Exit Equity'],
                    (candidate_data['Entry EV'] - candidate_data['Entry Equity']) - (candidate_data['Exit EV'] - candidate_data['Exit Equity'])
                ]
            }
            lbo_summary_df = pd.DataFrame(lbo_summary_data)
            fig = px.bar(lbo_summary_df, x='Component', y='Value', text_auto='.2s')
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Screening Criteria Analysis")
            st.markdown(f"""
            - **Stable Cash Flows:** Revenue CAGR of `{candidate_data['Revenue CAGR']:.1%}` (Threshold: >{st.session_state.criteria['MIN_REVENUE_CAGR_5Y']:.0%})
            - **Reasonable Valuation:** Entry EV/EBITDA multiple of `{candidate_data['EV/EBITDA']:.2f}x` (Threshold: <{st.session_state.criteria['MAX_EV_EBITDA_MULTIPLE']:.1f}x)
            - **Sufficient Debt Capacity:** Current Net Debt/EBITDA of `{candidate_data['Net Debt/EBITDA']:.2f}x` (Threshold: <{st.session_state.criteria['MAX_NET_DEBT_EBITDA']:.1f}x)
            - **Low Capital Intensity:** CapEx as % of Sales is `{candidate_data['CapEx as % of Sales']:.1%}` (Threshold: <{st.session_state.criteria['MAX_CAPEX_AS_PERCENT_OF_SALES']:.0%}).
            """)

            st.subheader("Returns Sensitivity Analysis")
            if selected_ticker in sensitivity_results:
                irr_table = sensitivity_results[selected_ticker]['IRR']
                moic_table = sensitivity_results[selected_ticker]['MOIC']
                
                col1, col2 = st.columns(2)
                with col1:
                    fig = go.Figure(data=go.Heatmap(
                        z=irr_table.values, x=irr_table.columns, y=irr_table.index,
                        colorscale='Greens', text=irr_table.applymap(lambda x: f'{x:.1%}'),
                        texttemplate="%{text}", textfont={"size":10}))
                    fig.update_layout(title_text='<b>IRR Sensitivity</b>', yaxis_title='Entry Multiple', xaxis_title='Exit Multiple')
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = go.Figure(data=go.Heatmap(
                        z=moic_table.values, x=moic_table.columns, y=moic_table.index,
                        colorscale='Blues', text=moic_table.applymap(lambda x: f'{x:.2f}x'),
                        texttemplate="%{text}", textfont={"size":10}))
                    fig.update_layout(title_text='<b>MOIC Sensitivity</b>', yaxis_title='Entry Multiple', xaxis_title='Exit Multiple')
                    st.plotly_chart(fig, use_container_width=True)

            st.subheader("Historical Financial Statements")
            if selected_ticker in financial_statements_dict:
                statements = financial_statements_dict[selected_ticker]
                tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow Statement"])
                with tab1:
                    st.dataframe(statements['Income Statement'].style.format("{:,.0f}", na_rep="-"))
                with tab2:
                    st.dataframe(statements['Balance Sheet'].style.format("{:,.0f}", na_rep="-"))
                with tab3:
                    st.dataframe(statements['Cash Flow'].style.format("{:,.0f}", na_rep="-"))
            else:
                st.warning("Could not retrieve detailed financial statements for this company.")
