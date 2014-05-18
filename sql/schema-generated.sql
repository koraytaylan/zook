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

drop table if exists period cascade;
create table period (
    id bigserial not null,
    session_id bigint,
    data json,
    key int not null default 0,
    phase int not null default 0,
    cost decimal not null default 0,
    skip_phase bool not null default false
);
alter table period add constraint pk_period primary key (id);

drop table if exists group cascade;
create table group (
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
alter table group add constraint pk_group primary key (id);

