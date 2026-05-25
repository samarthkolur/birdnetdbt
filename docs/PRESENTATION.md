# Presentation Notes

Steps to demo the project locally:

1. Start Postgres: `make up` (requires Docker).
2. Install Python deps: `python3 -m pip install -r requirements.txt`.
3. Load seed: `make seed` (creates `raw.bird_features`).
4. Run dbt: `make dbt-run` then `make dbt-test`.
5. Run ML demo: `make ml-mlp` and `make ml-ae` to train MLP and autoencoder.

Suggested talking points:
- Explain medallion layers (staging -> cleaning -> marts).
- Show `dbt docs generate` (optional) and `dbt run` logs.
- Run `dbt test` to show data quality enforcement.
- Show model outputs: `select * from public.bird_distribution limit 10;`
