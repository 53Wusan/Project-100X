import pandas as pd
import numpy as np
import os
from datetime import datetime
import yfinance as yf # Import yfinance

class DataHub:
    def __init__(self, data_path="project100x/data/raw"):
        self.data_path = data_path
        os.makedirs(self.data_path, exist_ok=True)

    def _download_ohlcv(self, ticker, start_date: str, end_date: str):
        print(f"Downloading real OHLCV data for {ticker} from {start_date} to {end_date} using yfinance...")
        try:
            df = yf.download(ticker, start=start_date, end=end_date)
            if df.empty:
                print(f"No data downloaded for {ticker}. Generating simulated data as fallback.")
                return self._generate_simulated_ohlcv(ticker, start_date, end_date) # Fallback to simulated data
            df.index.name = 'Date'
            return df
        except Exception as e:
            print(f"Error downloading data for {ticker}: {e}. Generating simulated data as fallback.")
            return self._generate_simulated_ohlcv(ticker, start_date, end_date) # Fallback to simulated data

    def _generate_simulated_ohlcv(self, ticker, start_date: str, end_date: str):
        print(f"Generating simulated OHLCV data for {ticker} for {start_date} to {end_date}...")
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Initial price for the ticker
        initial_price = np.random.uniform(50, 200)
        
        # Generate a base price trend (e.g., slightly upward with some randomness)
        price_series = [initial_price]
        for _ in range(1, len(dates)):
            # Introduce a slight upward drift and some noise
            next_price = price_series[-1] * (1 + np.random.uniform(-0.005, 0.01))
            price_series.append(next_price)
        
        prices = np.array(price_series)
        
        # Generate Open, High, Low, Close based on the generated price series
        # Ensure High >= Open, High >= Close, Low <= Open, Low <= Close
        open_prices = prices * (1 + np.random.uniform(-0.002, 0.002, len(dates)))
        close_prices = prices * (1 + np.random.uniform(-0.002, 0.002, len(dates)))
        
        high_prices = np.maximum(open_prices, close_prices) * (1 + np.random.uniform(0.001, 0.005, len(dates)))
        low_prices = np.minimum(open_prices, close_prices) * (1 - np.random.uniform(0.001, 0.005, len(dates)))
        
        # Ensure High is always greater than or equal to Open and Close
        high_prices = np.maximum(high_prices, np.maximum(open_prices, close_prices))
        # Ensure Low is always less than or equal to Open and Close
        low_prices = np.minimum(low_prices, np.minimum(open_prices, close_prices))

        # Volume (can be more sophisticated, but random for now)
        volume = np.random.randint(100000, 10000000, len(dates))
        
        data = {
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': volume
        }
        df = pd.DataFrame(data, index=dates)
        df.index.name = 'Date'
        return df

    def get_ohlcv_data(self, ticker, start_date: str, end_date: str):
        file_path = os.path.join(self.data_path, f"{ticker}.csv")
        if not os.path.exists(file_path):
            df = self._download_ohlcv(ticker, start_date, end_date)
            df.to_csv(file_path)
        else:
            df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
            # Ensure the data covers the requested range
            df_filtered = df[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))].copy() # Add .copy() to avoid SettingWithCopyWarning
            if df_filtered.empty: # If filtered data is empty or does not cover the full range
                print(f"Cached data for {ticker} does not fully cover {start_date} to {end_date}. Attempting to download or regenerate.")
                df = self._download_ohlcv(ticker, start_date, end_date)
                if not df.empty:
                    df.to_csv(file_path) # Overwrite with full downloaded data
                    df_filtered = df[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))].copy()
                else:
                    # Fallback to current filtered data if new download failed and original df had some data
                    print(f"Download failed again. Using existing partial data or empty if none.")
            df = df_filtered
        return df

if __name__ == '__main__':
    data_hub = DataHub()
    qqq_data = data_hub.get_ohlcv_data('QQQ', '2020-01-01', '2020-01-05')
    print(qqq_data.head())