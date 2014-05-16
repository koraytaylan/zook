create or replace function fn_session_start(key uuid) returns session as $$
<<fn>>
declare
    s session;
    ss subject;
begin
    select * into ss from fn_session_get_subjects(key);
    update session s
            set s.is_started = true,
                s.is_finished = false
        where s.key = key
        returning s.* into s;
    return s;
end
$$ language plpgsql;