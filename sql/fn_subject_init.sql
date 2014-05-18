create or replace function fn_subject_init(session_id bigint) returns subject as $$
<<fn>>
declare
    s session;
    p period;
    subject subject;
begin
    select * into s from session where id = session_id;

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