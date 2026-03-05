from collections import defaultdict
from typing import Dict, List


def target_exposure(score: int) -> float:
    if score == 3:
        return 1.0
    if score == 2:
        return 0.5
    return 0.0


def generate_trade_plan(current_weights: Dict[str, float], picks: List[dict], macro_score: int, max_delta: float = 0.2, max_weight_per_position: float = 0.4) -> dict:
    exposure = target_exposure(macro_score)
    n = len(picks) if picks else 1
    base_weight = exposure / n
    targets = defaultdict(float)
    for i, p in enumerate(picks):
        w = base_weight
        if i == 0 and macro_score == 3 and p["momentum"] > 0.1:
            w = min(max_weight_per_position, base_weight + 0.1)
        targets[p["ticker"]] = w

    draft = []
    all_tickers = set(current_weights.keys()) | set(targets.keys())
    for t in all_tickers:
        delta = targets.get(t, 0) - current_weights.get(t, 0)
        constrained = max(-max_delta, min(max_delta, delta))
        action = "观察"
        if constrained > 0.001:
            action = "加仓"
        elif constrained < -0.001:
            action = "减仓" if targets.get(t, 0) > 0 else "清仓"
        draft.append({"ticker": t, "current_weight": current_weights.get(t, 0), "target_weight": targets.get(t, 0), "delta_weight": constrained, "action": action})

    return {"draft": draft, "final": draft, "constraints": {"max_delta": max_delta}}
