-- Analytical mart: top species by recording count
select * from (
  select
    species,
    count(*) as recordings_count,
    dense_rank() over (order by count(*) desc) as rank
  from {{ ref('clean_bird_features') }}
  group by species
) t
where rank <= 10
order by recordings_count desc
