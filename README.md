# birdnetdbt

This repository contains a dbt project implementing the "Noise-Aware Indian Bird Sound Classification" pipeline staging and analytical marts described in the project report `DBT.pdf`.

See `README.dbt.md` for the full local setup details. The most common commands are below.

## Quick Run

Start Postgres:

```bash
make up
```

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Load the real iBC53 seed data:

```bash
source .venv/bin/activate
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/birdnet
bash scripts/load_seed.sh "$DATABASE_URL"
```

Run dbt:

```bash
source .venv/bin/activate
dbt run --profiles-dir . --project-dir .
dbt test --profiles-dir . --project-dir .
```

Run the ML demos:

```bash
make ml-mlp
make ml-ae
```

Render the dbt lineage graph:

```bash
make graph
```

Generate docs:

```bash
dbt docs generate --profiles-dir . --project-dir .
```

If you want the step-by-step walkthrough, command variants, and notes for Docker/Postgres, open [README.dbt.md](README.dbt.md).

