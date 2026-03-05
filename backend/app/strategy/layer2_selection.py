from typing import List, Dict

from app.data_adapters.yfinance_provider import YFinanceProvider
from app.strategy.indicators import momentum_13_26w, regression_slope, sma


def select_candidates(modules: List, top_k: int = 5, max_leaders: int = 2) -> List[Dict]:
    provider = YFinanceProvider()
    scored = []
    leaders = 0
    for m in modules:
        if not m.enabled:
            continue
        weekly = provider.history(m.leveraged_symbol, period="3y", interval="1wk")
        if weekly.empty or len(weekly) < 30:
            continue
        ma20 = sma(weekly["Close"], 20)
        trend_ok = weekly["Close"].iloc[-1] > ma20.iloc[-1] and regression_slope(ma20.dropna(), 5) > 0
        if not trend_ok:
            continue
        mom = momentum_13_26w(weekly["Close"])
        scored.append({"ticker": m.leveraged_symbol, "module": m.name, "momentum": mom, "kind": "etf"})
        if m.leader_symbol and leaders < max_leaders:
            lw = provider.history(m.leader_symbol, period="3y", interval="1wk")
            if not lw.empty and len(lw) > 30:
                lma20 = sma(lw["Close"], 20)
                ltrend = lw["Close"].iloc[-1] > lma20.iloc[-1] and regression_slope(lma20.dropna(), 5) > 0
                if ltrend:
                    scored.append({"ticker": m.leader_symbol, "module": m.name, "momentum": momentum_13_26w(lw["Close"]), "kind": "leader"})
                    leaders += 1
    return sorted(scored, key=lambda x: x["momentum"], reverse=True)[:top_k]
