-- Analytical mart: statistical summaries per species
select
  species,
  avg(duration_ms) as avg_duration_ms,
  stddev_pop(duration_ms) as stddev_duration_ms,
  avg(amplitude_db) as avg_amplitude_db,
  avg(confidence_score) as avg_confidence
from {{ ref('clean_bird_features') }}
group by species
order by avg_duration_ms desc
