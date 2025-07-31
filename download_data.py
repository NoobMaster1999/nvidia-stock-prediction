
import yfinance as yf
import pandas as pd

# Define the ticker symbol for NVIDIA
ticker_symbol = "NVDA"

# Download historical data
# You can adjust the start and end dates as needed
start_date = "2000-01-01"
end_date = "2025-07-31"

nvda_data = yf.download(ticker_symbol, start=start_date, end=end_date)

# Save the data to a CSV file
nvda_data.to_csv("NVDA_historical_data.csv")

print("NVIDIA historical data downloaded and saved to NVDA_historical_data.csv")


