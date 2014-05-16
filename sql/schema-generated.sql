drop table if exists session cascade;
create table session (
    id bigserial not null,
    period_id bigint,
    data json,
    key uuid not null,
    cost_low decimal not null default 3.0,
    cost_high decimal not null default 5.5,
    quantity_max int not null default 10,
    time_for_input int not null default 0,
    time_for_result int not null default 0,
    time_for_preparation int not null default 0,
    group_size int not null default 6,
    group_count int not null default 3,
    starting_balance decimal not null default 12.0,
    show_up_fee decimal not null default 5.0,
    maximum_loss decimal not null default 20.0,
    input_min decimal not null default 0,
    input_max decimal not null default 4.0,
    input_step_size decimal not null default 0.1,
    input_step_time int not null default 1,
    AInitQ int[],
    ADirectionPhase1 int[],
    AValuesParamSets int[],
    AValues decimal[],
    AValueUp decimal[],
    is_started bool not null default false,
    is_finished bool not null default false
);
alter table session add constraint pk_session primary key (id);

drop table if exists phase cascade;
create table phase (
    id bigserial not null,
    session_id bigint,
    data json,
    key int not null default 0,
    is_skipped bool not null default false
);
alter table phase add constraint pk_phase primary key (id);

drop table if exists period cascade;
create table period (
    id bigserial not null,
    phase_id bigint,
    data json,
    key int not null default 0,
    cost decimal not null default 0
);
alter table period add constraint pk_period primary key (id);

drop table if exists subject_group cascade;
create table subject_group (
    id bigserial not null,
    period_id bigint,
    data json,
    key int not null default 0,
    stage int not null default 0,
    direction int not null default 0,
    quantity_initial int not null default 0,
    quantity_reached int not null default 0,
    quantity_up int not null default 0,
    quantity_down int not null default 0,
    bid_diff_up decimal not null default 222,
    bid_diff_down decimal not null default 222,
    up_covered int not null default -2,
    sum_provides decimal not null default 0,
    sum_halvers int not null default 0,
    sum_bids decimal not null default 0,
    sum_asks decimal not null default 0,
    coin_flip int not null default 0,
    outcome int not null default 0,
    label_continue varchar(100) not null default 'Continue',
    is_finished bool not null default false
);
alter table subject_group add constraint pk_subject_group primary key (id);

drop table if exists subject cascade;
create table subject (
    id bigserial not null,
    session_id bigint,
    subject_group_id bigint,
    data json,
    key uuid not null,
    name varchar(100),
    previous_state int not null default 0,
    state int not null default 0,
    role int not null default 0,
    my_cost decimal not null default 0,
    my_value decimal not null default 0,
    my_bid decimal not null default -1,
    my_ask decimal not null default -1,
    my_tax decimal not null default -1,
    my_rebate decimal not null default -1,
    my_provide decimal not null default -1,
    current_balance decimal not null default 0,
    tent_profit decimal not null default 0,
    period_profit decimal not null default 0,
    phase_profit decimal not null default 0,
    total_profit decimal not null default 0,
    aft_profit decimal not null default 0,
    example_cost decimal not null default 0,
    default_provide decimal not null default 0,
    time_left decimal not null default 0,
    value_up decimal not null default 0,
    value_down decimal not null default 0,
    is_initialized bool not null default false,
    is_suspended bool not null default false,
    is_robot bool not null default false
);
alter table subject add constraint pk_subject primary key (id);

drop table if exists transaction cascade;
create table transaction (
    id bigserial not null,
    subject_id bigint,
    period_id bigint,
    data json,
    amount decimal not null default 0
);
alter table transaction add constraint pk_transaction primary key (id);

drop table if exists option cascade;
create table option (
    name varchar(100) not null,
    value json not null
);
alter table option add constraint pk_option primary key (name);

alter table session add constraint fk_session_period foreign key (period_id) references period (id);
alter table phase add constraint fk_phase_session foreign key (session_id) references session (id);
alter table period add constraint fk_period_phase foreign key (phase_id) references phase (id);
alter table subject_group add constraint fk_subject_group_period foreign key (period_id) references period (id);
alter table subject add constraint fk_subject_session foreign key (session_id) references session (id);
alter table subject add constraint fk_subject_subject_group foreign key (subject_group_id) references subject_group (id);
alter table transaction add constraint fk_transaction_subject foreign key (subject_id) references subject (id);
alter table transaction add constraint fk_transaction_period foreign key (period_id) references period (id);


create index ix_session_key on session (key);
create index ix_phase_key on phase (key);
create index ix_period_key on period (key);
create index ix_subject_group_key on subject_group (key);
create index ix_subject_key on subject (key);
create index ix_subject_session_id on subject (session_id);

