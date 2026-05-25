-- Analytical mart: species distribution
select
  species,
  count(*) as recordings_count,
  round(100.0 * count(*) / sum(count(*)) over (), 4) as pct_of_total
from {{ ref('clean_bird_features') }}
group by species
order by recordings_count desc
