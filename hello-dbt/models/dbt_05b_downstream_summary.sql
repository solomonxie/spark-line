-- Step 5b: `ref()` — dbt's core idea, and the one deliberate exception to
-- this project's "every model stands alone" rule. This model doesn't know
-- or care where dbt_05a_upstream_orders lives (view or table, dev or prod
-- schema) — `ref()` resolves that at compile time, and also tells dbt to
-- build 05a first if it hasn't been already.
--
-- Run (the `+` pulls in 05a automatically):
--     dbt run --select +dbt_05b_downstream_summary
select
    city,
    count(*) as order_count,
    sum(amount) as total_amount
from {{ ref('dbt_05a_upstream_orders') }}
group by city
order by city
