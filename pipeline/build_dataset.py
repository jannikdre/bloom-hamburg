"""Orchestriert die Pipeline und schreibt frontend/public/data/current.json."""
from __future__ import annotations

import datetime as dt
import json
import os

from enrich_images import enrich
from fetch_dwd import fetch_blooming
from fetch_harvest import fetch_harvest

HERE = os.path.dirname(__file__)
OUT = os.path.normpath(
    os.path.join(HERE, "..", "frontend", "public", "data", "current.json")
)


def main() -> None:
    today = dt.date.today()
    iso_year, iso_week, _ = today.isocalendar()

    print("1/4 DWD-Phänologie (Blüte)…")
    blooming = fetch_blooming(today)
    print("2/4 Saisonkalender (Ernte)…")
    harvesting = fetch_harvest(today)
    print("3/4 Wikipedia-Anreicherung…")
    blooming = enrich(blooming, with_text=True)
    harvesting = enrich(harvesting, with_text=False)

    # interne Felder (_start, _n, wiki) vor dem Schreiben entfernen
    def clean(items, keys):
        for it in items:
            for k in list(it):
                if k not in keys:
                    it.pop(k)
        return items

    blooming = clean(
        blooming,
        {"name_de", "name_lat", "image", "image_credit", "text", "source"},
    )
    harvesting = clean(
        harvesting,
        {"name_de", "image", "image_credit", "months", "note", "source"},
    )

    data = {
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "week": iso_week,
        "region": "Hamburg",
        "blooming": blooming,
        "harvesting": harvesting,
    }

    print(f"4/4 Schreibe {OUT}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Fertig: {len(blooming)} blühend, {len(harvesting)} erntereif (KW {iso_week}).")


if __name__ == "__main__":
    main()
