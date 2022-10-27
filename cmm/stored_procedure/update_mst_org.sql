create or replace procedure update_cmm_org()
language plpgsql
as $$
declare
begin
   -- 組織マスタの親コードを設定する(mext)
   with data as (
      select code
            ,id
            ,substring(code, 1, 5) || REGEXP_REPLACE(substring(code, 6), '(00000)+$', '') truncated
            ,dense_rank() over(order by length(substring(code, 1, 5) || REGEXP_REPLACE(substring(code, 6), '(00000)+$', ''))) rnk
        from cmm_organization
   ), data_with_parent as (
   select d.code
         ,d.id
         ,d.rnk
         ,d.truncated
         ,p.code parent_org
         ,p.truncated
         ,p.id pid
   from data d
   left join data p
      on d.code like p.truncated || '%'
      and p.rnk = (select max(sub.rnk)
                     from data sub
                  where sub.code < d.code
                     and sub.rnk < d.rnk
                     and d.code like sub.truncated || '%')
                   order by 1)
   -- select * from data_with_parent order by 1
   update cmm_organization main
      set parent_org_id = d.pid
         -- ,rank = d.rnk
      from data_with_parent d
      where d.id = main.id
   ;

   update cmm_organization
      set parent_org_id = (select id
                             from cmm_organization
                            where code = '000000000000000000000000000000'
                              -- and now() between valid_from and valid_through
                          )
   where parent_org_id is null
   and code != '000000000000000000000000000000';

   -- update cmm_organization
   --    set rank = 0
   --  where code = '000000000000000000000000000000';
end; $$
