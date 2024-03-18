-- Step 5a: an "upstream" model — nothing special on its own, just data
-- for step 5b to build on via ref(). See dbt_05b_downstream_summary.sql.
select * from (
    values
        (1, 'Toronto', 42.50),
        (2, 'Miami', 18.00),
        (3, 'Toronto', 9.75)
) as t(order_id, city, amount)
