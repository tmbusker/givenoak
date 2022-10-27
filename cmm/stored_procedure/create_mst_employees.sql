create or replace procedure create_cmm_employees()
language plpgsql
as $$
declare
begin
    with csv as (
      select c.職員番号 as code
            ,c.updater
            ,dense_rank() over(order by c.職員番号) rnk
        from mext_employeecsv c
    ), person as (
      select p.last_name || ' ' || p.first_name name
            ,p.last_name_kana || ' ' || p.first_name_kana kana
            ,p.email
            ,dense_rank() over(order by p.last_name || ' ' || p.first_name, p.email) rnk
        from cmm_person p
    )
    insert into cmm_employee (
         id
        ,create_time
        ,creator
        ,update_time
        ,updater
        ,name
        ,name_kana
        ,code
        ,employ_date
        ,email
        ,version
    )
    select nextval('cmm_employee_id_seq')
          ,now()
          ,'create_cmm_employees'
          ,now()
          ,'create_cmm_employees'
          ,p.name
          ,p.kana
          ,c.code
          ,c.valid_from
          ,p.email
          ,1
      from csv c
     inner join person p
        on c.rnk = p.rnk
      left join cmm_employee e
        on c.valid_from = e.valid_from
       and c.code = e.code
     where e.code is null
;

update cmm_authuser u
   set username = e.code
  from cmm_employee e
 where e.email = u.email
;

insert into cmm_org_member (
     id
    ,version
    ,create_time
    ,creator
    ,update_time
    ,updater
    ,is_main_duty
    ,is_manager
    ,is_staff
    ,employee_id
    ,organization_id
)
select nextval('cmm_org_member_id_seq')
      ,1
      ,now()
      ,'create_cmm_employees'
      ,now()
      ,'create_cmm_employees'
      ,case when honmu.code is not null then true else false end
      ,false
      ,false
      ,e.id
      ,coalesce(honmu.id, heinin.id)
  from mext_employeecsv c
 inner join cmm_employee e
    on c.職員番号 = e.code
  left join cmm_organization honmu
    on c.本務組織 = honmu.code
  left join cmm_organization heinin
    on c.本務組織 = heinin.code
    and (honmu.code is not null or heinin.code is not null)
;

end; $$