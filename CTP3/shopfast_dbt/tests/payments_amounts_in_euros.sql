-- Same lab limits as CTP2: a 100x cents mistake must fail.
select
    min(amount) as smallest_amount,
    max(amount) as largest_amount,
    avg(amount) as mean_amount,
    median(amount) as median_amount
from {{ ref('stg_payments') }}
having count(*) = 0
    or count(amount) <> count(*)
    or min(amount) < 0.01
    or max(amount) > 5000
    or avg(amount) not between 20 and 500
    or median(amount) not between 20 and 400
