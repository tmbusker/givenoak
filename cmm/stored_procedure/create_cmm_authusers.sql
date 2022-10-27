create or replace procedure create_cmm_authusers()
language plpgsql
as $$
declare
begin
    insert into cmm_authuser (
         id
        ,password
        ,is_superuser
        ,username
        ,first_name
        ,last_name
        ,email
        ,is_staff
        ,is_active
        ,date_joined
    )
    select nextval('cmm_authuser_id_seq')
          ,'password'
          ,false
          ,'user' || p.id
          ,p.first_name
          ,p.last_name
          ,p.email
          ,false
          ,true
          ,now()
      from cmm_person p
      left join cmm_authuser u
        on u.username = 'user' || p.id
     where u.username is null
;
end; $$