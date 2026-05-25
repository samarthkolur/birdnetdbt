-- Create raw schema and table for seed import
create schema if not exists raw;
create table if not exists raw.bird_features (
  recording_id text primary key,
  species text,
  confidence double precision,
  duration_ms int,
  amplitude_db double precision,
  pitch_hz double precision,
  sample_rate int,
  embeddings_json jsonb
);
