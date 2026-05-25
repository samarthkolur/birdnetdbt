-- Cleaning model: enforce basic quality constraints
with staged as (
    select * from {{ ref('stg_bird_features') }}
)

select
        recording_id,
        species,
        confidence_score,
        duration_ms,
        amplitude_db,
        pitch_hz,
        sample_rate,
        embedding
from staged
where embedding is not null
    and confidence_score is not null
    and confidence_score >= 0.25
    and duration_ms between 100 and 10000
    and amplitude_db is not null
    -- ensure embedding contains dims array
    and jsonb_typeof(embedding->'dims') = 'array'

