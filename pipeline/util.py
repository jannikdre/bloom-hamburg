"""Gemeinsame Helfer: Download mit lokalem Cache + Haversine-Distanz.

Bewusst nur Python-Standardbibliothek (urllib), damit die Pipeline auch unter
dem hier vorhandenen Python 3.8 ohne phenodata/pandas läuft.
"""
from __future__ import annotations

import hashlib
import math
import os
import time
import urllib.request

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
USER_AGENT = "bloom-hamburg/0.1 (+https://github.com; data pipeline)"


def fetch(url: str, *, cache_ttl: float = 6 * 3600, binary: bool = False):
    """Lädt eine URL, mit einfachem Datei-Cache (TTL in Sekunden).

    Gibt bei binary=False latin-1-dekodierten Text zurück (DWD-CSV-Kodierung),
    sonst rohe Bytes.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = hashlib.sha1(url.encode()).hexdigest()
    path = os.path.join(CACHE_DIR, key)
    if os.path.exists(path) and (time.time() - os.path.getmtime(path)) < cache_ttl:
        with open(path, "rb") as f:
            data = f.read()
    else:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(path, "wb") as f:
            f.write(data)
    return data if binary else data.decode("latin-1")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
