create or replace function fn_session_start(id bigint) returns session as $$
<<fn>>
declare
    s session;
    ss subject;
begin
    select * into ss from fn_session_get_subjects(id);

    with _ss as (select * from fn_session_get_subjects(id))
    update subject
        set state = 100 --active
    from subject _s
        inner join _ss on _ss.id = _s.id;

    update session
            set is_started = true,
                is_finished = false
        --from session ses
        where session.id = id
        returning * into s;
    return s;
end
$$ language plpgsql;