with
    ue as (
        select id as event_id, user_id, type as event_type, time as event_time
        from sandbox_landing.user_event
    )
select *
from ue
