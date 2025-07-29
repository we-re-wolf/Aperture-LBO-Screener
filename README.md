Aperture: The Data-Driven LBO Screening Platform
Aperture is a sophisticated, Python-based financial analysis platform designed to automate the core private equity workflow of proprietary deal sourcing. It systematically screens a universe of public companies to identify promising Leveraged Buyout (LBO) candidates, runs an automated LBO model on each, and presents the findings in a professional, interactive dashboard.

This project moves beyond the execution-focused mindset of an analyst to the idea-generation and investment-thesis-driven mindset of a private equity associate, demonstrating the ability to think critically like a principal investor.


🚀 Core Features
Aperture is a complete, end-to-end toolkit that transforms raw market data into actionable investment insights.

Interactive Screening Control Panel: A dynamic sidebar allows users to adjust all key LBO screening criteria in real-time (e.g., max valuation multiple, min growth rate, max leverage). The candidate list updates instantly, enabling powerful scenario analysis.

High-Performance Data Engine: A multi-threaded data pipeline efficiently sources and processes market data (yfinance) and multi-year financial statements (from SEC 10-K filings via sec-api) for a large universe of companies.

Robust Financial Metrics Engine: A heuristic-based calculator intelligently parses financial statements, handling non-standard line items to accurately compute key metrics like Revenue CAGR, EBITDA Margin stability, and Capital Intensity.

Automated LBO Modeling: For every company that passes the screen, the platform automatically runs a simplified LBO model to calculate the two most important private equity return metrics: Internal Rate of Return (IRR) and Multiple on Invested Capital (MOIC).

Professional Investment Memo Dashboard: The Streamlit frontend presents a ranked shortlist of the top LBO candidates. Selecting a candidate reveals a detailed "Tear Sheet" with:

Key return metrics and transaction assumptions.

Visualizations of the LBO structure (Sources & Uses) and value creation.

A summary of why the company passed the screening criteria.

A full sensitivity analysis showing how IRR and MOIC change with different entry/exit multiples.

Tabbed views of the company's complete historical financial statements.

🛠️ Tech Stack & Architecture
Aperture is built with a modular architecture, ensuring that each component of the analysis pipeline is independent and robust.

Language: Python 3.10+

Frontend: Streamlit

Data Analysis: Pandas, NumPy

Data Sourcing:

yfinance: For real-time market data.

sec-api: For sourcing SEC filings and parsing XBRL financial data.

Visualization: Plotly Express

Project Structure:

/Aperture/
|-- /src/
|   |-- /connectors/     # Modules for connecting to external APIs
|   |-- /screening/      # Metrics Calculator and Screener engines
|   |-- /modeling/       # The automated LBO model logic
|-- /data/
|   |-- /universe/       # CSV file with the list of tickers to screen
|-- app.py               # The main Streamlit application
|-- requirements.txt     # Project dependencies
|-- README.md            # This file

⚙️ Local Setup and Installation
Follow these steps to set up and run the Aperture application on your local machine.

1. Prerequisites
Python 3.10 or higher

A git client

2. Clone the Repository
git clone [https://github.com/your-username/Aperture.git](https://github.com/your-username/Aperture.git)
cd Aperture

3. Set Up a Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies.

# Create the virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

4. Install Dependencies
Install all the required Python libraries using the requirements.txt file.

pip install -r requirements.txt

5. Configure API Keys
Aperture requires a free API key from sec-api.io to source financial statements.

Open the configuration file: src/config.py

SEC API Key:

Go to sec-api.io and register for a free API key.

Paste your key into the SEC_API_KEY variable.

6. Run the Application
Once the setup is complete, you can launch the Streamlit web application.

streamlit run app.py

Your web browser will automatically open a new tab with the running application.

🚀 How to Use
Launch the application.

Click the "▶️ Start / Refresh Data Pipeline" button. The app will fetch and process data for all companies in the universe (this may take a few minutes).

Use the Control Panel in the sidebar to adjust the screening criteria. The shortlist of candidates will update instantly.

Select a company from the "Investment Memo Tear Sheet" dropdown to view its detailed LBO analysis.