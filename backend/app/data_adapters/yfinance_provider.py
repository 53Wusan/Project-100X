from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


class YFinanceProvider:
    def history(self, symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
        df = df.rename(columns=str.title)
        return df

    def recent_30d(self, symbol: str) -> pd.DataFrame:
        end = datetime.utcnow().date()
        start = end - timedelta(days=45)
        df = yf.download(symbol, start=start, end=end, interval="1d", auto_adjust=True, progress=False)
        return df.tail(30)
