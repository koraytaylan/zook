create or replace function fn_session_start(key uuid) returns session as $$
<<fn>>
declare
    ses session;
begin
    update session
        set is_started = true,
            is_finished = false
    return ses;
end
$$ language plpgsql;