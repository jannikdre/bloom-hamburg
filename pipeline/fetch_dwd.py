"""DWD-Phänologie (Sofortmelder) → 'aktuell in Blüte' für die Region Hamburg.

Logik:
  - Stationen per Radius um Hamburg filtern (robuster als Bundesland, da die
    Stadt selbst wenige Phänologie-Stationen hat).
  - Pro Art (species_map.json) die Sofortmelder-Datei laden, Phase 5
    (Blüte Beginn) im laufenden Jahr an regionalen Stationen suchen.
  - 'Aktuell in Blüte', wenn der mediane Blühbeginn <= heute <= Blühbeginn +
    geschätzte Blühdauer (bloom_days) liegt.
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import json
import os
import statistics
from typing import Dict, List

from util import fetch, haversine_km

HERE = os.path.dirname(__file__)
STATIONS_URL = (
    "https://opendata.dwd.de/climate_environment/CDC/help/"
    "PH_Beschreibung_Phaenologie_Stationen_Sofortmelder.txt"
)
WILD_RECENT = (
    "https://opendata.dwd.de/climate_environment/CDC/observations_germany/"
    "phenology/immediate_reporters/wild/recent/"
)

HAMBURG_LAT, HAMBURG_LON = 53.55, 9.99
RADIUS_KM = 60.0
PHASE_BLUEHBEGINN = 5


def _rows(text: str):
    """DWD-CSV: ';'-getrennt, Felder mit Whitespace gepolstert, Zeilenende 'eor'."""
    reader = csv.reader(io.StringIO(text), delimiter=";")
    for row in reader:
        yield [c.strip() for c in row]


def load_regional_station_ids() -> Dict[int, dict]:
    text = fetch(STATIONS_URL, cache_ttl=7 * 24 * 3600)
    out: Dict[int, dict] = {}
    rows = _rows(text)
    next(rows, None)  # Header
    for r in rows:
        if len(r) < 11 or not r[0]:
            continue
        try:
            sid = int(r[0])
            lat = float(r[2])
            lon = float(r[3])
        except ValueError:
            continue
        if haversine_km(HAMBURG_LAT, HAMBURG_LON, lat, lon) <= RADIUS_KM:
            out[sid] = {"name": r[1], "lat": lat, "lon": lon, "bundesland": r[10]}
    return out


def _bloom_starts(text: str, station_ids: set, year: int) -> List[dt.date]:
    """Blühbeginn-Daten (Phase 5) des laufenden Jahres an regionalen Stationen."""
    starts: List[dt.date] = []
    rows = _rows(text)
    next(rows, None)  # Header
    for r in rows:
        if len(r) < 6:
            continue
        try:
            sid = int(r[0])
            phase = int(r[4])
            datum = r[5]
        except ValueError:
            continue
        if phase != PHASE_BLUEHBEGINN or sid not in station_ids:
            continue
        try:
            d = dt.datetime.strptime(datum, "%Y%m%d").date()
        except ValueError:
            continue
        if d.year == year:
            starts.append(d)
    return starts


def fetch_blooming(today: dt.date | None = None) -> List[dict]:
    today = today or dt.date.today()
    stations = load_regional_station_ids()
    station_ids = set(stations.keys())
    print(f"  Regionale Sofortmelder-Stationen (<= {RADIUS_KM:.0f} km): {len(station_ids)}")

    with open(os.path.join(HERE, "species_map.json"), encoding="utf-8") as f:
        species = json.load(f)["wild"]

    blooming: List[dict] = []
    for sp in species:
        try:
            text = fetch(WILD_RECENT + sp["file"], cache_ttl=12 * 3600)
        except Exception as e:  # noqa: BLE001 - einzelne Art darf nicht alles kippen
            print(f"  ! {sp['name_de']}: Download-Fehler ({e})")
            continue
        starts = _bloom_starts(text, station_ids, today.year)
        if not starts:
            continue
        median_start = sorted(starts)[len(starts) // 2]
        window_end = median_start + dt.timedelta(days=sp.get("bloom_days", 30))
        if median_start <= today <= window_end:
            blooming.append(
                {
                    "name_de": sp["name_de"],
                    "name_lat": sp["name_lat"],
                    "wiki": sp.get("wiki"),
                    "source": "DWD",
                    "_start": median_start.isoformat(),
                    "_n": len(starts),
                }
            )
            print(f"  ✓ {sp['name_de']}: Blühbeginn ~{median_start} ({len(starts)} Beob.)")
    blooming.sort(key=lambda b: b["_start"], reverse=True)
    return blooming


if __name__ == "__main__":
    for b in fetch_blooming():
        print(b)
