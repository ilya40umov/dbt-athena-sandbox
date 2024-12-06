with
    u as (select * from {{ ref("dim_users") }}),
    ue as (select * from {{ ref("fct_user_events") }})
select
    u.user_id, u.user_name, ue.event_type, date(ue.event_time) as event_date, count() as event_count
from u
left join ue on u.user_id = ue.user_id
group by 1, 2, 3, 4
