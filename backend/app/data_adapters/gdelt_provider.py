from datetime import datetime, timedelta
from typing import List

import requests


class GDELTProvider:
    BASE = "https://api.gdeltproject.org/api/v2/doc/doc"

    def fetch(self, keyword: str, max_records: int = 8) -> List[dict]:
        start = (datetime.utcnow() - timedelta(days=5)).strftime("%Y%m%d%H%M%S")
        end = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        params = {
            "query": keyword,
            "mode": "ArtList",
            "maxrecords": max_records,
            "format": "json",
            "startdatetime": start,
            "enddatetime": end,
        }
        r = requests.get(self.BASE, params=params, timeout=20)
        r.raise_for_status()
        articles = r.json().get("articles", [])
        out = []
        for a in articles:
            title = a.get("title", "")
            risk = "high" if any(w in title.lower() for w in ["war", "ban", "crash", "probe"]) else "neutral"
            sent = -0.5 if risk == "high" else 0.1
            out.append(
                {
                    "title": title,
                    "source": a.get("sourceCommonName", "gdelt"),
                    "published_at": a.get("seendate"),
                    "url": a.get("url", ""),
                    "sentiment": sent,
                    "risk_label": risk,
                }
            )
        return out
