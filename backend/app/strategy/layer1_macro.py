from dataclasses import dataclass

from app.data_adapters.yfinance_provider import YFinanceProvider
from app.strategy.indicators import regression_slope, sma


@dataclass
class MacroState:
    macro_score: int
    regime: str
    trend_ok: int
    vol_ok: int
    breadth_ok: int
    reason_text: str


def compute_macro_state(breadth_mode: str = "A") -> MacroState:
    provider = YFinanceProvider()
    spy_w = provider.history("SPY", period="3y", interval="1wk")
    vix_w = provider.history("^VIX", period="1y", interval="1wk")
    vix3m_w = provider.history("^VIX3M", period="1y", interval="1wk")

    trend_ok = int(spy_w["Close"].iloc[-1] > sma(spy_w["Close"], 40).iloc[-1]) if len(spy_w) >= 40 else 0

    if not vix3m_w.empty:
        vol_ok = int(vix_w["Close"].iloc[-1] < vix3m_w["Close"].iloc[-1])
        vol_reason = "VIX<VIX3M"
    else:
        vol_ok = int(vix_w["Close"].iloc[-1] < 25)
        vol_reason = "fallback VIX<25"

    breadth_ok = 0
    if breadth_mode == "A":
        nyad = provider.history("^NYAD", period="2y", interval="1wk")
        if not nyad.empty:
            breadth_ok = int(regression_slope(nyad["Close"], 10) > 0)
    score = trend_ok + vol_ok + breadth_ok
    regime = "Risk-On" if score == 3 else "Caution" if score == 2 else "Risk-Off"
    return MacroState(
        macro_score=score,
        regime=regime,
        trend_ok=trend_ok,
        vol_ok=vol_ok,
        breadth_ok=breadth_ok,
        reason_text=f"trend={trend_ok}, vol={vol_ok}({vol_reason}), breadth={breadth_ok}",
    )
