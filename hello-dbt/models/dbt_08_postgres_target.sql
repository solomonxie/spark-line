-- Step 8 (capstone): the same model style as step 2, meant to run against
-- a real Postgres warehouse instead of local DuckDB — the optional EC2
-- node from ../terraform + ../ansible (see ../README.md).
--
-- Run:
--     dbt run --select dbt_08_postgres_target --target postgres
select * from (
    values
        ('Toronto', 18.5),
        ('Miami', 29.1),
        ('Reykjavik', 7.2),
        ('Singapore', 31.0)
) as t(city, temperature_c)
