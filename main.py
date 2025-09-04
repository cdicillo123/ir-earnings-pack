import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_earnings_data(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/earnings"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    tables = soup.find_all("table")
    if not tables:
        return pd.DataFrame()
    df = pd.read_html(str(tables[0]))[0]
    return df

def save_to_csv(df, ticker):
    filename = f"{ticker}_earnings.csv"
    df.to_csv(filename, index=False)
    print(f"Saved: {filename}")

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL"]
    for ticker in tickers:
        df = fetch_earnings_data(ticker)
        if not df.empty:
            save_to_csv(df, ticker)