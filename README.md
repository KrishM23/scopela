# SCOPE LA · Oral health access gaps

Maps dental access gaps in Los Angeles City Council Districts 8, 9, and 10.

## Local

```bash
./serve.sh
```

Open http://127.0.0.1:8787

## Netlify

Publish directory: `site` (see `netlify.toml`).

## Data

- `site/data/districts.geojson` — district boundaries + metrics
- `site/data/metrics.json` — city averages and focus districts
- `data/district_oral_health.json` — analysis table

```bash
python3 analysis/oral_health_disparities.py
python3 analysis/generate_figures.py
```

## Sources

CDC PLACES via Civic Data Atlas, ACS 2020–24, LA County CCHP, LA County Oral Health Chartbook, UCSF Healthforce Center, City of Los Angeles council district boundaries.
