-- Step 1: the simplest possible model — a view over a literal row.
--
-- Run:
--     dbt run --select dbt_01_hello_model
select 1 as id, 'hello from dbt' as message
