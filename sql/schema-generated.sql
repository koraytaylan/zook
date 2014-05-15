drop table if exists session cascade;
create table session (
    id bigserial not null,
    phase_id bigserial not null,
    period_id bigserial not null,
    data json,
    key uuid not null,
    cost_low float not null default 3.0,
    cost_high float not null default 5.5,
    quantity_max int not null default 10,
    time_for_input int not null default 0,
    time_for_result int not null default 0,
    time_for_preparation int not null default 0,
    group_size int not null default 6,
    group_count int not null default 3,
    starting_balance float not null default 12.0,
    show_up_fee float not null default 5.0,
    maximum_loss float not null default 20.0,
    input_min float not null default 0,
    input_max float not null default 4.0,
    input_step_size float not null default 0.1,
    input_step_time int not null default 1,
    AInitQ int[12] not null,
    ADirectionPhase1 int[12] not null,
    AValuesParamSets int[4][24] not null,
    AValues float[4][6][11] not null,
    AValueUp float[4][6][11] not null,
    is_started bool not null,
    is_finished bool not null
);
alter table session add constraint pk_session primary key (id);

drop table if exists phase cascade;
create table phase (
    id bigserial not null,
    session_id bigserial not null,
    data json,
    key int not null default 0,
    is_skipped bool not null
);
alter table phase add constraint pk_phase primary key (id);

drop table if exists period cascade;
create table period (
    id bigserial not null,
    phase_id bigserial not null,
    data json,
    key int not null default 0,
    cost float not null default 0
);
alter table period add constraint pk_period primary key (id);

drop table if exists subject_group cascade;
create table subject_group (
    id bigserial not null,
    data json,
    key int not null default 0,
    stage int not null default 0,
    direction int not null default 0,
    quantity_initial int not null default 0,
    quantity_reached int not null default 0,
    quantity_up int not null default 0,
    quantity_down int not null default 0,
    bid_diff_up float not null default 222,
    bid_diff_down float not null default 222,
    up_covered int not null default -2,
    sum_provides float not null default 0,
    sum_halvers int not null default 0,
    sum_bids float not null default 0,
    sum_asks float not null default 0,
    coin_flip int not null default 0,
    outcome int not null default 0,
    label_continue varchar(100) not null default 'Continue',
    is_finished bool not null
);
alter table subject_group add constraint pk_subject_group primary key (id);

drop table if exists subject cascade;
create table subject (
    id bigserial not null,
    session_id bigserial not null,
    subject_group_id bigserial not null,
    data json,
    field varchar(100),
    previous_state int not null default 0,
    state int not null default 0,
    role int not null,
    my_cost float not null default 0,
    my_bid float not null default -1,
    my_ask float not null default -1,
    my_tax float not null default -1,
    my_rebate float not null default -1,
    my_provide float not null default -1,
    current_balance float not null default 0,
    tent_profit float not null default 0,
    period_profit float not null default 0,
    phase_profit float not null default 0,
    total_profit float not null default 0,
    aft_profit float not null default 0,
    example_cost float not null default 0,
    default_provide float not null default 0,
    time_left float not null default 0,
    value_up float not null default 0,
    value_down float not null default 0,
    is_initialized bool not null,
    is_suspended bool not null,
    is_robot bool not null
);
alter table subject add constraint pk_subject primary key (id);

drop table if exists subject_balance cascade;
create table subject_balance (
    id bigserial not null,
    subject_id bigserial not null,
    session_id bigserial not null,
    data json,
    amount float not null default 0
);
alter table subject_balance add constraint pk_subject_balance primary key (id);

alter table session add constraint fk_session_phase foreign key (phase_id) references phase (id);
alter table session add constraint fk_session_period foreign key (period_id) references period (id);
alter table phase add constraint fk_phase_session foreign key (session_id) references session (id);
alter table period add constraint fk_period_phase foreign key (phase_id) references phase (id);

alter table subject add constraint fk_subject_session foreign key (session_id) references session (id);
alter table subject add constraint fk_subject_subject_group foreign key (subject_group_id) references subject_group (id);
alter table subject_balance add constraint fk_subject_balance_subject foreign key (subject_id) references subject (id);
alter table subject_balance add constraint fk_subject_balance_session foreign key (session_id) references session (id);

create index ix_session_key on session (key);
create index ix_phase_key on phase (key);
create index ix_period_key on period (key);
create index ix_subject_group_key on subject_group (key);

