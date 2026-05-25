#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/load_seed.sh postgresql://user:pass@host:port/dbname
URL=${1:-}
if [ -z "$URL" ]; then
  echo "Provide DATABASE_URL as first arg, e.g. postgresql://postgres:postgres@localhost:5432/birdnet"
  exit 2
fi

psql "$URL" -f scripts/init_raw_schema.sql

# prefer generated iBC53 CSV if present
if [ -f data/ibc53_features.csv ]; then
  CSV=data/ibc53_features.csv
elif [ -f data/seed_bird_features.csv ]; then
  CSV=data/seed_bird_features.csv
else
  echo "No seed CSV found in data/ - run scripts/extract_ibc53_embeddings.py first"
  exit 2
fi

psql "$URL" -c "\copy raw.bird_features FROM '${CSV}' CSV HEADER"

echo "Seed loaded into raw.bird_features from ${CSV}"
