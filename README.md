# RetailPulse — AI-Powered Customer Analytics & Demand Forecasting

A portfolio-ready Streamlit starter app inspired by the RetailPulse dark AI command-center Figma design.

## Features in this starter
- Five pages: Executive Overview, Demand Forecasting, Customer Analytics, Inventory Intelligence, Model Monitoring
- Dark theme with reusable KPI and AI-insight UI helpers
- Interactive Plotly charts and filters
- Sample daily sales, synthetic customer, and inventory datasets
- A transparent moving-average baseline forecast
- Rule-based inventory reorder recommendations
- Clear labels for synthetic data and placeholder model-monitoring metrics

## Run locally
Use Python 3.10+ (recommended).

```bash
# 1. Open a terminal in the RetailPulse folder
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Streamlit will print a local URL, usually http://localhost:8501.

## Project structure
```text
RetailPulse/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── retail_sales.csv
│   ├── customers.csv
│   └── inventory.csv
└── src/
    └── (place future forecasting / ML modules here)
```

## Dataset notes
- `retail_sales.csv`: daily product-level units, price, revenue, stock snapshot, and promotion flag from 2025-01-01 through 2026-09-30.
- `customers.csv`: synthetic customer segments, orders, spend, recency, average order value, and a synthetic churn label.
- `inventory.csv`: current synthetic stock snapshot, trailing 30-day average demand, lead time, safety stock, reorder point, and inventory value.

The data is generated for demonstration and is not real customer or retailer data. Since daily sales are aggregated by product and date, transaction-level order count and AOV are estimated in the dashboard. Replace the synthetic churn labels with a real target definition before model training. Forecast-monitoring values are placeholders until an actual model evaluation pipeline is added.
