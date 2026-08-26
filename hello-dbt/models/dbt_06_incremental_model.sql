-- Step 6: incremental models. On the first run this builds the full
-- table; on every later run, only the `is_incremental()` branch applies,
-- so dbt isn't reprocessing the whole source each time.
--
-- The source here is static, so run this twice to see the effect: the
-- first run inserts 3 rows; the second inserts 0, since
-- `event_id > max(existing)` is now true for none of them — exactly what
-- incremental is supposed to do when nothing new has actually arrived.
--
-- Run:
--     dbt run --select dbt_06_incremental_model
--     dbt run --select dbt_06_incremental_model   # again — 0 rows added
{{ config(materialized='incremental', unique_key='event_id') }}

select * from (
    values
        (1, 'signup', current_timestamp),
        (2, 'purchase', current_timestamp),
        (3, 'signup', current_timestamp)
) as t(event_id, event_type, created_at)

{% if is_incremental() %}
where event_id > (select coalesce(max(event_id), 0) from {{ this }})
{% endif %}
