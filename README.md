# 📈 StockAnalysis Dashboard

An interactive Python dashboard to analyse and visualise stock data, sentiment from financial headlines, and statistical indicators such as volatility and trade volume significance. This tool integrates Yahoo Finance and Alpha Vantage APIs with a tkinter-based GUI and matplotlib visualisations.

---

## 🚀 Features

- Fetch historical stock prices using Yahoo Finance
- Calculate volatility and perform t-tests on trade volume
- Scrape recent financial headlines via Finviz
- Run sentiment analysis on headlines using VADER
- Visualise mean adjusted close prices over time
- Search for ticker suggestions using Alpha Vantage
- GUI interface for a user-friendly experience

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/stock-analysis-dashboard.git
   cd stock-analysis-dashboard
2. **Install Dependencies:**

   pip install -r requirements.txt

3. Add your Alpha Vantage API key:

   Open the Python file and replace:

   self.api_key = 'ENTER YOUR OWN API KEY HERE'

   with your actual API key from Alpha Vantage.
