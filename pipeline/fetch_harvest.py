"""Saisonkalender → 'aktuell Erntezeit' für den laufenden Monat."""
from __future__ import annotations

import datetime as dt
import json
import os
from typing import List

HERE = os.path.dirname(__file__)


def fetch_harvest(today: dt.date | None = None) -> List[dict]:
    today = today or dt.date.today()
    month = today.month
    with open(os.path.join(HERE, "seasonal_vegetables.json"), encoding="utf-8") as f:
        items = json.load(f)["items"]

    out: List[dict] = []
    for it in items:
        if month in it["months"]:
            out.append(
                {
                    "name_de": it["name_de"],
                    "wiki": it.get("wiki"),
                    "months": it["months"],
                    "note": it.get("note", ""),
                    "source": "Saisonkalender",
                }
            )
    out.sort(key=lambda x: x["name_de"])
    print(f"  ✓ {len(out)} Gemüse-/Obstarten im Monat {month}")
    return out


if __name__ == "__main__":
    for h in fetch_harvest():
        print(h)
