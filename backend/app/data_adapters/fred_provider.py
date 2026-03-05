import os
from typing import Dict

import requests


class FREDProvider:
    BASE = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("FRED_KEY", "")

    def latest(self, series_id: str) -> Dict:
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 1,
        }
        r = requests.get(self.BASE, params=params, timeout=20)
        r.raise_for_status()
        data = r.json().get("observations", [])
        return data[0] if data else {"value": None}
