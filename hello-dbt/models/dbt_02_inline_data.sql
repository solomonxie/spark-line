-- Step 2: a small inline dataset via VALUES. Every model in this project
-- builds its own data this way instead of `ref()`-ing a shared seed, so
-- each one stays runnable entirely on its own (step 5 is the exception —
-- see its comment for why).
--
-- Run:
--     dbt run --select dbt_02_inline_data
select * from (
    values
        ('Toronto', 18.5),
        ('Miami', 29.1),
        ('Reykjavik', 7.2),
        ('Singapore', 31.0)
) as t(city, temperature_c)
