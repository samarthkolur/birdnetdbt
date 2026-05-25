.PHONY: up seed dbt-run dbt-test ml-mlp ml-ae graph clean

up:
	docker-compose up -d

seed:
	python3 -m pip install -r requirements.txt
	./scripts/load_seed.sh postgresql://postgres:postgres@localhost:5432/birdnet

dbt-run:
	dbt run --profiles-dir . --project-dir .
	dbt docs generate --profiles-dir . --project-dir .

dbt-test:
	dbt test --profiles-dir . --project-dir .
	dbt docs generate --profiles-dir . --project-dir .

ml-mlp:
	python3 ml/train_mlp.py

ml-ae:
	python3 ml/train_autoencoder.py

graph:
	python3 scripts/render_dbt_lineage.py

clean:
	docker-compose down -v
