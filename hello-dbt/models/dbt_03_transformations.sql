-- Step 3: derived columns and conditional logic — the SQL-model
-- equivalent of ../spark-helloworld/hello_04_transformations.py.
--
-- Run:
--     dbt run --select dbt_03_transformations
with cities as (
    select * from (
        values
            ('Toronto', 18.5),
            ('Miami', 29.1),
            ('Reykjavik', 7.2),
            ('Singapore', 31.0)
    ) as t(city, temperature_c)
)

select
    city,
    temperature_c,
    case
        when temperature_c < 10 then 'cold'
        when temperature_c < 25 then 'mild'
        else 'hot'
    end as climate_band
from cities
order by temperature_c desc
