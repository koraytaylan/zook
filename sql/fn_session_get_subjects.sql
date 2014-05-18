create or replace function fn_session_get_subjects(id bigint) returns setof subject as $$
<<fn>>
declare
    subjects subject;
begin
    select ss.* into subjects
        from subject ss
        where ss.session_id = id 
            and ss.state between 100 and 199;

    select * from subjects;
end
$$ language plpgsql;