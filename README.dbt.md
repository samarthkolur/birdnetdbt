# birdnet_dbt - local development

Quick steps:

1. Start Postgres locally (docker-compose):

```bash
docker-compose up -d
```

2. Install dependencies (recommended inside a venv):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Load seed data into Postgres (example uses psql):

```bash
psql postgresql://postgres:postgres@localhost:5432/birdnet -c "\copy raw.bird_features FROM 'data/seed_bird_features.csv' CSV HEADER;"
```

4. Run dbt:

```bash
dbt run --profiles-dir . --project-dir .
dbt test --profiles-dir . --project-dir .
```

5. Generate docs (optional):

```bash
dbt docs generate --profiles-dir . --project-dir .
dbt docs serve --profiles-dir . --project-dir .
```

Notes:
- Copy `profiles.yml.example` to your `~/.dbt/profiles.yml` or pass `--profiles-dir .`.
- The project assumes a `raw.bird_features` source table; use the seed CSV or your own import.
