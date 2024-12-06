{{ config(materialized="incremental") }}
with
    u as (select * from {{ ref("dim_users") }}),
    ue as (select * from {{ ref("src_user_events") }})
select ue.*
from ue
right join u on ue.user_id = u.user_id
{% if is_incremental() %}
    where
        ue.event_time
        > (select coalesce(max(event_time), timestamp '1900-01-01') from {{ this }})
{% endif %}
