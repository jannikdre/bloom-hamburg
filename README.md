# Hamburg blüht & erntet 🌼🥕

Eine kleine PWA, die wöchentlich zeigt, **welche Pflanzen aktuell in der Region
Hamburg blühen** und **welches Gemüse/Obst gerade Saison hat**.

- **Blüh-Daten:** echte Phänologie-Beobachtungen des Deutschen Wetterdiensts
  (DWD, Sofortmelder, Open Data), gefiltert auf Stationen im ~60-km-Umkreis um Hamburg.
- **Erntedaten:** kuratierter, monatsbasierter Saisonkalender für Norddeutschland
  (`pipeline/seasonal_vegetables.json`).
- **Bilder & Kurztexte:** Wikipedia/Wikimedia Commons.

## Architektur

Statische Daten-Pipeline + statisches Frontend (kein laufender Server):

```
[GitHub Actions, wöchentlich]  ──►  pipeline/build_dataset.py
   DWD-Phänologie + Saisonkalender + Wikipedia
        └─► frontend/public/data/current.json (committet)
                 └─► Vite/React-Frontend (PWA)  ─►  GitHub Pages
```

## Projektstruktur

```
pipeline/    Python-Datenpipeline (nur Standardbibliothek, kein pip nötig)
frontend/    React + Vite + Tailwind, eigener Service Worker (PWA)
.github/workflows/deploy.yml   Daten erzeugen + bauen + Pages-Deploy (1 Job)
```

## Lokal entwickeln

```bash
# 1) Daten erzeugen → frontend/public/data/current.json
cd pipeline && python3 build_dataset.py

# 2) Frontend starten
cd ../frontend && npm install && npm run dev

# Produktions-Build lokal testen (inkl. PWA/Service Worker):
npm run build && npm run preview
```

## Deployment (GitHub Pages)

Push nach `main` (oder der wöchentliche Cron / manueller `workflow_dispatch`)
löst `deploy.yml` aus: Pipeline läuft, aktualisiert `current.json`, baut das
Frontend mit `VITE_BASE=/<repo>/` und veröffentlicht auf GitHub Pages.

Einmalig in den Repo-Settings: **Pages → Source = GitHub Actions** aktivieren.

## Quellen & Lizenzen

- Phänologie: © Deutscher Wetterdienst (DWD), Open Data.
- Bilder/Texte: Wikipedia/Wikimedia Commons – Urheber & Lizenz werden pro Bild
  in der App angezeigt (überwiegend CC-BY / CC-BY-SA bzw. Public Domain).
- Saisonkalender: eigene Kuratierung auf Basis öffentlicher Saisonangaben.
