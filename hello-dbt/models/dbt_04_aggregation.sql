-- Step 4: aggregation — group by + count/avg/max.
--
-- Run:
--     dbt run --select dbt_04_aggregation
with trips as (
    select * from (
        values
            ('Manhattan', 2.4, 12.0),
            ('Manhattan', 5.1, 22.0),
            ('Brooklyn', 0.8, 6.0),
            ('Brooklyn', 12.3, 40.0),
            ('Queens', 3.6, 15.0)
    ) as t(borough, trip_distance, fare_amount)
)

select
    borough,
    count(*) as total_trips,
    round(avg(trip_distance), 2) as avg_distance,
    round(max(fare_amount), 2) as max_fare
from trips
group by borough
order by borough
