create or replace function fn_session_proceed(session_id bigint) returns session as $$
<<fn>>
declare
    s session;
    p period;
    ss subject;
begin
    select * into ss from fn_session_get_subjects(session_id);

    update subject
        set state = 100 --active
    from subject s
        inner join ss on ss.id = s.id;

    update session s
            set s.is_started = true,
                s.is_finished = false
        where s.key = key
        returning s.* into s;

    return s;
end
$$ language plpgsql;