-- Step 7: a custom Jinja macro — reusable SQL, called like a function.
-- See ../macros/celsius_to_fahrenheit.sql.
--
-- Run:
--     dbt run --select dbt_07_macros
select
    city,
    temperature_c,
    round({{ celsius_to_fahrenheit('temperature_c') }}, 1) as temperature_f
from (
    values
        ('Toronto', 18.5),
        ('Miami', 29.1),
        ('Reykjavik', 7.2),
        ('Singapore', 31.0)
) as t(city, temperature_c)
