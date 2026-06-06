"""Anreicherung über Wikipedia/Wikimedia Commons: Bild-URL, Kurztext, Lizenz.

- de.wikipedia MediaWiki-API: Thumbnail + Intro-Extrakt + Dateiname.
- Commons imageinfo/extmetadata: Urheber + Lizenz (für CC-BY-Attribution).
Ergebnisse werden über den URL-Cache in util.fetch gepuffert.
"""
from __future__ import annotations

import json
import re
import urllib.parse
from typing import List, Optional

from util import fetch

WP_API = "https://de.wikipedia.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
TAG_RE = re.compile(r"<[^>]+>")
PLACEHOLDER = "https://placehold.co/600x400/8FBF6F/ffffff?text="


def _get_json(api: str, params: dict) -> dict:
    url = api + "?" + urllib.parse.urlencode(params)
    raw = fetch(url, cache_ttl=7 * 24 * 3600, binary=True).decode("utf-8")
    return json.loads(raw)


def _trim(text: str, limit: int = 320) -> str:
    text = text.strip().replace("\n", " ")
    if len(text) <= limit:
        return text
    cut = text[:limit]
    dot = cut.rfind(". ")
    return (cut[: dot + 1] if dot > 80 else cut.rstrip() + " …")


def _license_credit(file_name: Optional[str]) -> str:
    if not file_name:
        return "Wikimedia Commons"
    try:
        data = _get_json(
            COMMONS_API,
            {
                "action": "query", "format": "json", "prop": "imageinfo",
                "iiprop": "extmetadata", "titles": "File:" + file_name,
            },
        )
        pages = data["query"]["pages"]
        meta = next(iter(pages.values()))["imageinfo"][0]["extmetadata"]
        artist = TAG_RE.sub("", meta.get("Artist", {}).get("value", "")).strip()
        artist = re.sub(r"\s+", " ", artist).strip()
        # extmetadata liefert den Urheber gelegentlich doppelt ("XXXXXX") → halbieren
        half = len(artist) // 2
        if artist and len(artist) % 2 == 0 and artist[:half] == artist[half:]:
            artist = artist[:half]
        lic = meta.get("LicenseShortName", {}).get("value", "").strip()
        bits = []
        if artist:
            bits.append(artist)
        bits.append("Wikimedia Commons")
        if lic:
            bits.append(lic)
        return " / ".join(bits)
    except Exception:  # noqa: BLE001
        return "Wikimedia Commons"


def _enrich_one(title: str):
    data = _get_json(
        WP_API,
        {
            "action": "query", "format": "json", "redirects": "1",
            "prop": "pageimages|extracts", "piprop": "thumbnail|name",
            "pithumbsize": "600", "exintro": "1", "explaintext": "1",
            "titles": title,
        },
    )
    page = next(iter(data["query"]["pages"].values()))
    thumb = page.get("thumbnail", {}).get("source")
    file_name = page.get("pageimage")
    extract = page.get("extract", "")
    return thumb, file_name, extract


def enrich(items: List[dict], with_text: bool) -> List[dict]:
    for it in items:
        title = it.get("wiki")
        thumb = file_name = None
        extract = ""
        if title:
            try:
                thumb, file_name, extract = _enrich_one(title)
            except Exception as e:  # noqa: BLE001
                print(f"  ! Wiki-Fehler für {title}: {e}")
        it["image"] = thumb or (PLACEHOLDER + urllib.parse.quote(it["name_de"]))
        it["image_credit"] = (
            _license_credit(file_name) if thumb else "Platzhalterbild"
        )
        if with_text:
            base = _trim(extract) if extract else f"{it['name_de']} – aktuell in der Region in Blüte."
            start = it.get("_start")
            if start:
                y, m, d = start.split("-")
                base += f" (Blühbeginn in der Region beobachtet ab {d}.{m}.{y}.)"
            it["text"] = base
    return items
