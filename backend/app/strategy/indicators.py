import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()


def roc(series: pd.Series, window: int) -> pd.Series:
    return series.pct_change(window)


def momentum_13_26w(close: pd.Series) -> float:
    return float(0.5 * roc(close, 13).iloc[-1] + 0.5 * roc(close, 26).iloc[-1])


def regression_slope(series: pd.Series, window: int = 10) -> float:
    y = series.tail(window).values
    if len(y) < window:
        return 0.0
    x = np.arange(len(y))
    return float(np.polyfit(x, y, 1)[0])


def ad_line_from_net_adv(net_adv: pd.Series) -> pd.Series:
    return net_adv.cumsum()


def mcclellan_oscillator(net_adv: pd.Series) -> pd.Series:
    return net_adv.ewm(span=19, adjust=False).mean() - net_adv.ewm(span=39, adjust=False).mean()


def classify_stage(close: pd.Series, ma_short: int = 10, ma_long: int = 20) -> str:
    ma_s = sma(close, ma_short)
    ma_l = sma(close, ma_long)
    if close.iloc[-1] > ma_l.iloc[-1] and ma_s.iloc[-1] > ma_l.iloc[-1]:
        return "主升"
    if close.iloc[-1] < ma_l.iloc[-1] and ma_s.iloc[-1] < ma_l.iloc[-1]:
        return "急跌"
    return "震荡"
