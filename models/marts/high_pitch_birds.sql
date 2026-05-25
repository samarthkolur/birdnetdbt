-- Analytical mart: species with high average pitch
select species, avg(pitch_hz) as avg_pitch_hz
from {{ ref('clean_bird_features') }}
where pitch_hz is not null
group by species
having avg(pitch_hz) > 5000
order by avg_pitch_hz desc
