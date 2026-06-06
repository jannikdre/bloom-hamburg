# Plan: Hamburg "Was blüht & was wird geerntet" App

## Context

Du möchtest eine App, die wöchentlich aktualisiert zeigt:
1. **Welche Pflanzen aktuell in der Region Hamburg in Blüte stehen** – mit Bild & Info.
2. **Welches Gemüse aktuell in der Region geerntet wird** – als Übersicht.

Wichtige Rahmenbedingungen (mit dir geklärt):
- Es ist eine **komplett neue App**. Das aktuelle `jga-planner`-Repo enthält einen Junggesellenabschieds-Planer und bleibt unberührt. Die Umsetzung erfolgt **später in einem neuen lokalen Root-Ordner**. Dieser Plan ist daher konzeptionell/architektonisch.
- Blüh-Daten kommen aus **DWD Live-Phänologiedaten** (Open Data).
- Der wöchentliche Update-Job läuft über **GitHub Actions Cron**.
- **Online gehostet & vom Smartphone unterwegs nutzbar** → Hosting als **statisches Frontend + PWA** (auf dem Handy-Homescreen installierbar). Kostenlos, schnell, offline-tauglich. Begründung siehe unten.

### Warum statisch + PWA (Hosting-Entscheidung)
Die Daten sind **für alle Nutzer identisch** und ändern sich **nur wöchentlich** – nichts wird pro Nutzer gespeichert oder live berechnet. Damit ist ein laufender Server (wie Fly.io beim JGA-Planner, der eine schreibende DB pro Nutzer hat) überflüssig. Der **User-Impact** der statischen Variante: sofortiges Öffnen vom Homescreen, letzte Daten bleiben auch ohne Netz sichtbar (PWA-Cache), 0 € Kosten, praktisch wartungsfrei. Ein Backend (Fly.io) lohnt erst, falls später nutzerspezifische Features dazukommen (Login, Favoriten) – dann kann nachgerüstet werden.

### Recherche-Erkenntnisse (entscheidend für die Architektur)
- **DWD Phänologie Open Data** (`opendata.dwd.de/.../phenology/`) liefert echte beobachtete Phasen (z. B. *Blühbeginn*, *Blühende*) für **wildwachsende Pflanzen** und einige **Feldfrüchte**. Die Untergruppe `immediate_reporters` ("Sofortmelder") meldet Ereignisse zeitnah → ideal für „aktuell in Blüte". Daten + Referenzdateien (Phasen, Objekte/Arten, Stationen mit Geo-Koordinaten & Bundesland) sind frei als CSV verfügbar. Die Python-Lib **`phenodata`** kapselt den Download bequem.
- **DWD hat KEINE Gemüse-Erntedaten** (nur wenige Feldfrüchte wie Weizen/Mais). Für „welches Gemüse wird gerade geerntet" gibt es **keine öffentliche API** → realistischster Weg: ein **gepflegter, monatsbasierter Saisonkalender als JSON** (Datenbasis: Verbraucherzentrale / BZfE / regional-saisonal).
- **Bilder & Kurzinfos**: Wikipedia/Wikimedia Commons REST-API per Artname (deutsch + lateinisch). Frei nutzbar, **Attribution (CC-BY) erforderlich**.

## Empfohlene Architektur

**Static-Data-Pipeline + statisches Frontend** (einfachste, günstigste, am besten zu „wöchentlich via GitHub Actions" passende Lösung – kein dauerhaft laufendes Backend nötig):

```
[GitHub Actions Cron, wöchentlich]
        │  (Python-Pipeline)
        ├─ DWD Phänologie laden  → "aktuell in Blüte"
        ├─ Saisonkalender (JSON) → "aktuell Erntezeit"
        ├─ Wikipedia/Commons     → Bilder-URLs + Kurztext + Lizenz
        └─ schreibt  data/current.json  → commit ins Repo
                                   │
                          [statisches React/Vite-Frontend liest current.json]
                                   │
                          Hosting: GitHub Pages / Netlify (kostenlos)
```

Warum statisch statt Backend: Die Daten ändern sich nur wöchentlich und sind für alle Nutzer identisch. Ein einmal pro Woche erzeugtes JSON reicht völlig – das spart Server, Datenbank und Kosten. (Das bekannte FastAPI+Fly.io-Setup aus `jga-planner` wäre möglich, ist hier aber Overkill.)

## Projektstruktur (neuer Root-Ordner, z. B. `bloom-hamburg/`)

```
bloom-hamburg/
├── pipeline/                      # Python-Datenpipeline (läuft in CI)
│   ├── fetch_dwd.py               # DWD-Phänologie laden + filtern (Region Hamburg)
│   ├── fetch_harvest.py           # Saisonkalender → aktueller Monat
│   ├── enrich_images.py           # Wikipedia/Commons: Bild-URL, Kurztext, Lizenz
│   ├── build_dataset.py           # orchestriert alles → data/current.json
│   ├── seasonal_vegetables.json   # kuratierter Gemüse-Saisonkalender (manuell gepflegt)
│   ├── species_map.json           # DWD-Objekt-ID → {de-Name, lat. Name, Wiki-Titel}
│   └── requirements.txt           # phenodata, httpx, pandas
├── data/
│   └── current.json               # generiertes Output (von CI committet)
├── frontend/                      # React + Vite + Tailwind (PWA-fähig)
│   ├── src/
│   │   ├── App.tsx                # Tabs: "In Blüte" / "Erntezeit"
│   │   ├── components/PlantCard.tsx
│   │   ├── data.ts                # lädt /data/current.json
│   │   └── types.ts
│   ├── package.json
│   └── vite.config.ts
└── .github/workflows/weekly-update.yml
```

## Umsetzungsschritte

### 1. Datenpipeline (Python)
- **`fetch_dwd.py`**: Phänologie `immediate_reporters` (wild + ggf. crops, `recent`) via `phenodata` oder Direkt-Download von `opendata.dwd.de`. Stationen über die DWD-Stationsliste auf Region Hamburg filtern (Bundesland = Hamburg/Schleswig-Holstein/Niedersachsen **oder** Umkreis ~50 km um 53.55, 9.99). „Aktuell in Blüte" = Arten, bei denen *Blühbeginn* (Phase) im laufenden Jahr eingetreten ist und *Blühende* noch nicht / geschätzte Blühdauer noch läuft (Bezug: aktuelle Kalenderwoche). Objekt-IDs über DWD-Referenzdatei + `species_map.json` auf Namen mappen.
- **`fetch_harvest.py`**: aus `seasonal_vegetables.json` die Einträge für den aktuellen Monat ziehen (Felder: Name, Monate, „Lager/Freiland"-Hinweis, Region).
- **`enrich_images.py`**: pro Art/Gemüse Wikipedia-REST-Summary (`de.wikipedia.org/api/rest_v1/page/summary/<Titel>`) → Thumbnail-URL + Extrakt; Lizenz/Attribution via Commons `imageinfo`. Ergebnisse cachen, um API-Last gering zu halten.
- **`build_dataset.py`**: alles zusammenführen → `data/current.json` mit Struktur:
  ```json
  {
    "generated_at": "...", "week": 23, "region": "Hamburg",
    "blooming":   [{"name_de","name_lat","image","image_credit","text","source":"DWD"}],
    "harvesting": [{"name_de","image","image_credit","months","note","source":"Saisonkalender"}]
  }
  ```

### 2. Frontend (React + Vite + Tailwind)
- Lädt `data/current.json`, zeigt zwei Tabs/Sektionen: **„Jetzt in Blüte"** und **„Erntezeit"**.
- `PlantCard`: Bild, deutscher + lat. Name, Kurztext, Quelle/Attribution, Monats-/Regionshinweis.
- „Stand: KW xx / Datum" anzeigen. UI auf Deutsch.
- **PWA-Setup** (Pflicht-Anforderung „unterwegs vom Smartphone"): `manifest.webmanifest` (Name, Icons, `display: standalone`, Theme-Farbe) + Service-Worker (z. B. via `vite-plugin-pwa`) mit Cache-Strategie für App-Shell und `current.json` → installierbar auf dem Homescreen, letzte Daten offline sichtbar. Responsive/Mobile-First-Layout.

### 3. Wöchentlicher Job (`.github/workflows/weekly-update.yml`)
- `on: schedule: cron` (1×/Woche, z. B. Montag früh) + `workflow_dispatch` (manuell).
- Schritte: Python-Setup → `pip install -r pipeline/requirements.txt` → `python pipeline/build_dataset.py` → `data/current.json` committen & pushen (nur bei Änderung). Push triggert das Frontend-Deploy (GitHub Pages/Netlify).

### 4. Hosting (festgelegt: statisch + PWA, kostenlos)
- **GitHub Pages oder Netlify** (statisch, kostenlos, HTTPS, CDN). Frontend-Build + `data/current.json` ausliefern.
- Custom Domain optional (beide Hoster unterstützen es kostenlos).
- Deploy-Trigger: Push auf `main` (durch den wöchentlichen Daten-Commit **oder** Code-Änderungen) baut & veröffentlicht automatisch.
- Zugriff: per URL im Browser; auf dem Smartphone über „Zum Startbildschirm hinzufügen" als PWA installierbar → App-ähnliche Nutzung unterwegs.
- Spätere Option (nur falls nutzerspezifische, schreibende Features dazukommen): Wechsel auf das bekannte Fly.io-Single-Container-Setup.

## Wichtige Hinweise / Risiken
- **Gemüse-Erntedaten**: bewusst kuratierter Kalender (keine Live-Quelle existiert). Pflegeaufwand: gelegentliche manuelle Updates der `seasonal_vegetables.json`.
- **DWD-Datenlatenz/Lücken**: Sofortmelder decken nicht jede Art lückenlos ab; Blühdauer wird teils geschätzt. Sinnvoll: Liste der beobachteten Arten kuratieren (`species_map.json`).
- **Bild-Lizenzen**: Attribution gemäß CC-BY immer mit anzeigen.
- **DWD-Nutzungsbedingungen** (Quellenangabe „Deutscher Wetterdienst") im Footer erwähnen.

## Verifikation (bei späterer Umsetzung)
1. `python pipeline/build_dataset.py` lokal laufen lassen → prüfen, dass `data/current.json` plausible Blüh- & Ernte-Einträge mit Bildern für die aktuelle KW enthält.
2. `cd frontend && npm run dev` → beide Tabs zeigen Karten mit Bildern korrekt an (Desktop + mobile Ansicht).
3. GitHub Action manuell via `workflow_dispatch` auslösen → prüfen, dass `current.json` committet und das Deploy aktualisiert wird.
4. Stichprobe: 2–3 Arten gegen die DWD-Website „Aktuelle Phänologie" gegenprüfen; Gemüse gegen den Saisonkalender.
