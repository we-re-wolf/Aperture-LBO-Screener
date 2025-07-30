# 📊 Aperture: The Data-Driven LBO Screening Platform

**Aperture** is a sophisticated, Python-based financial analysis platform designed to automate the core private equity workflow of proprietary deal sourcing. It systematically screens a universe of public companies to identify promising Leveraged Buyout (LBO) candidates, runs an automated LBO model on each, and presents the findings in a professional, interactive dashboard.

This project moves beyond the execution-focused mindset of an analyst to the idea-generation and investment-thesis-driven mindset of a private equity associate—demonstrating the ability to think critically like a principal investor.

---

## 🚀 Core Features

Aperture is a complete, end-to-end toolkit that transforms raw market data into actionable investment insights:

- **🎛 Interactive Screening Control Panel**  
  A dynamic sidebar allows users to adjust key LBO screening criteria in real time (e.g., max valuation multiple, min growth rate, max leverage). The candidate list updates instantly for powerful scenario analysis.

- **⚡ High-Performance Data Engine**  
  A multi-threaded pipeline efficiently sources and processes market data from `yfinance` and multi-year financial statements from SEC 10-K filings (via `sec-api`) for a large universe of companies.

- **📐 Robust Financial Metrics Engine**  
  A heuristic-based calculator parses financial statements, handling non-standard line items to accurately compute metrics like Revenue CAGR, EBITDA Margin stability, and Capital Intensity.

- **🤖 Automated LBO Modeling**  
  For every company that passes the screen, a simplified LBO model calculates two critical return metrics:
  - Internal Rate of Return (IRR)
  - Multiple on Invested Capital (MOIC)

- **📄 Professional Investment Memo Dashboard**  
  The Streamlit frontend presents:
  - A ranked shortlist of top LBO candidates  
  - A detailed "Tear Sheet" for each candidate, including:
    - Key return metrics and transaction assumptions
    - LBO structure visualizations (Sources & Uses, Value Creation)
    - Screening rationale
    - Full IRR & MOIC sensitivity analysis
    - Historical financial statements in tabbed views

---

## 🛠️ Tech Stack & Architecture

- **Language**: Python 3.10+
- **Frontend**: [Streamlit](https://streamlit.io)
- **Data Analysis**: Pandas, NumPy
- **Data Sourcing**:
  - [`yfinance`](https://github.com/ranaroussi/yfinance) for market data
  - [`sec-api`](https://sec-api.io) for SEC filing data
- **Visualization**: Plotly Express

### 📁 Project Structure

```
├── /src/
│   ├── /connectors/      # API connection modules
│   ├── /screening/       # Screener logic and metrics engine
│   ├── /modeling/        # LBO modeling logic
├── /data/
│   ├── /universe/        # CSV file with list of tickers
├── app.py                # Main Streamlit application
├── requirements.txt      # Project dependencies
├── README.md             # You’re reading it!
```

---

## ⚙️ Local Setup and Installation

Follow the steps below to set up and run Aperture locally.

### 1. Prerequisites

- Python 3.10 or higher  
- A Git client

### 2. Clone the Repository

```
git clone https://github.com/we-re-wolf/Aperture.git
cd Aperture
```

### 3. Set Up a Virtual Environment
```
# Create virtual environment
python -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

### 4. Install Dependencies
```
pip install -r requirements.txt
```

### 5. Configure API Keys

Aperture uses a free API key from sec-api.io to fetch financial statements.
	•	Open the file: src/config.py
	•	Paste your SEC API key into the SEC_API_KEY variable.
```
SEC_API_KEY = "your_api_key_here"
```

### 6. Run the Application
```
streamlit run app.py
```
Your default browser will open the app automatically.

### 🚀 How to Use
	1.	Launch the application using the above command.
	2.	Click the “▶️ Start / Refresh Data Pipeline” button to fetch and process data (may take a few minutes).
	3.	Use the Sidebar Control Panel to adjust screening filters. The candidate list updates live.
	4.	Select a company from the “Investment Memo Tear Sheet” to view its full LBO analysis.

### 💼 License & Contribution

This is an educational/development tool and not intended for financial advice or live trading.

Feel free to fork, improve, or contribute via pull requests. For questions, open an issue or reach out via GitHub Discussions.

### 📬 Contact

Created by Aritra Mondal
📧 [Email](mailto:aritramondal.work@gmail.com)
🔗 [LinkedIn](https://linkedin.com/in/aritramondal-in)

```
Let me know if you'd like me to tailor the contact info, add badges, or generate the `requirements.txt` file based on your current codebase.
```
