{{ config(materialized="table") }}
with u as (select * from {{ ref("src_users") }})
select *
from u
where u.user_name is not null and u.user_name != ''
