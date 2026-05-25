-- Analytical mart: species with long average duration
select species, avg(duration_ms) as avg_duration_ms
from {{ ref('clean_bird_features') }}
group by species
having avg(duration_ms) > 2500
order by avg_duration_ms desc
