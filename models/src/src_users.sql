with
    u as (
        select
            id as user_id,
            name as user_name,
            case when is_admin then 'ADMIN' else 'USER' end as user_type
        from sandbox_landing.user
    )
select *
from u
