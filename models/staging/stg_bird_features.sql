-- Staging model: standardise raw bird feature columns
with src as (
    select
        recording_id::text as recording_id,
        species::text as species,
        confidence::double precision as confidence_score,
        duration_ms::int as duration_ms,
        amplitude_db::double precision as amplitude_db,
        pitch_hz::double precision as pitch_hz,
        sample_rate::int as sample_rate,
        case
          when pg_typeof(embeddings_json) = 'jsonb'::regtype then embeddings_json
          else embeddings_json::jsonb
        end as embedding
    from {{ source('raw', 'bird_features') }}
)

select * from src
