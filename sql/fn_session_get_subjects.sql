create or replace function fn_session_get_subjects(key uuid) returns setof subject as $$
<<fn>>
declare
    subjects subject;
begin
    return query 
        select ss.*
        from subject ss
            inner join session s on s.id = ss.session_id
        where ss.state between 100 and 199;
end
$$ language plpgsql;