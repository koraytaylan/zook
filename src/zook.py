import tornado.web
import os
import handlers
import uuid
import random
import threading
import math


class Session(object):
    """docstring for Session"""

    def __init__(self):
        super(Session, self).__init__()
        self.key = str(uuid.uuid4())
        self.subjects = {}
        self.phases = {}
        self.phase = 0
        self.period = 0
        self.stage = 0
        self.is_started = False
        self.is_finished = False
        self.is_all_ready = False

        self.cost = 0
        self.cost_low = 3.0
        self.cost_high = 5.5
        self.quantity_max = 10  # Maximum feasible quantity
        self.input_min = 0
        self.input_max = 4

        self.time_for_input = 0
        self.time_for_result = 0
        self.time_for_preparation = 0

        # Group size
        self.group_size = 6
        self.group_size_min = 2
        self.group_size_max = 20

        # Group count
        self.group_count = 3
        self.group_count_min = 1
        self.group_count_max = 64

        # Starting balance
        self.starting_balance = 12
        self.starting_balance_min = 0
        self.starting_balance_max = 32
        self.starting_balance_incrementer = 0.25

        # Show up fee
        self.show_up_fee = 5
        self.show_up_fee_min = 0
        self.show_up_fee_max = 20
        self.show_up_fee_incrementer = 0.25

        # Maximum loss
        self.maximum_loss = 20
        self.maximum_loss_min = 0
        self.maximum_loss_max = 40
        self.maximum_loss_incrementer = 0.25

        # Bid and Ask steps
        self.input_step_size = 0.1
        self.input_step_time = 3
        self.input_step_max = 0

        self.AInitQ = (7, 5, 8, 4, 2, 6, 3, 5, 1, 2, 6, 4)
        self.ADirectionPhase1 = (1, 1, -1, 0, -1, 0, -1, 0, 1, 1, -1, 0)
        self.AValuesParamSets = (
            (
                2, 0, 2, 1, 3, 2, 3, 0, 1, 1, 3, 2,
                0, 2, 2, 1, 3, 1, 2, 0, 3, 1, 0, 3
            ),
            (
                0, 0, 2, 3, 3, 1, 1, 3, 1, 3, 0, 0,
                1, 3, 1, 1, 1, 0, 3, 0, 3, 1, 2, 2
            ),
            (
                0, 0, 1, 3, 1, 2, 3, 1, 0, 0, 3, 2,
                2, 3, 2, 2, 3, 2, 0, 1, 0, 1, 1, 3
            ),
            (
                3, 3, 2, 1, 0, 2, 2, 3, 0, 2, 2, 2,
                1, 2, 0, 3, 2, 2, 2, 1, 2, 0, 2, 1
            )
        )
        # Values for each phase(0..3), each role(0..5) and each quantity(0..10)
        self.AValues = (
            (
                (0, 1.42, 2.24, 2.82, 3.24, 3.54, 3.76, 3.9, 3.96, 3.96, 3.96),
                (0, 1.58, 3.00, 4.34, 5.52, 6.62, 7.56, 8.42, 9.12, 9.74, 10.20),
                (0, 1.82, 3.24, 4.34, 5.28, 6.06, 6.72, 7.26, 7.68, 7.98, 8.16),
                (0, 1.42, 2.44, 3.22, 3.80, 4.22, 4.56, 4.82, 5.00, 5.10, 5.12),
                (0, 1.42, 2.24, 2.82, 3.24, 3.54, 3.76, 3.90, 3.96, 3.96, 3.96),
                (0, 0.50, 0.84, 1.06, 1.20, 1.30, 1.32, 1.32, 1.32, 1.32, 1.32)
            ),
            (
                (0, 1.60, 2.60, 3.36, 3.96, 4.44, 4.84, 5.16, 5.40, 5.56, 5.64),
                (0, 1.76, 3.36, 4.88, 6.24, 7.52, 8.64, 9.68, 10.56, 11.36, 12.00),
                (0, 2.00, 3.60, 4.88, 6.00, 6.96, 7.80, 8.52, 9.12, 9.60, 9.96),
                (0, 1.60, 2.80, 3.76, 4.52, 5.12, 5.64, 6.08, 6.44, 6.72, 6.92),
                (0, 1.60, 2.60, 3.36, 3.96, 4.44, 4.84, 5.16, 5.40, 5.56, 5.64),
                (0, 0.68, 1.20, 1.60, 1.92, 2.20, 2.40, 2.56, 2.68, 2.76, 2.80)
            ),
            (
                (0, 2.00, 3.25, 4.20, 4.95, 5.55, 6.05, 6.45, 6.75, 6.95, 7.05),
                (0, 2.20, 4.20, 6.10, 7.80, 9.40, 10.80, 12.10, 13.20, 14.20, 15.00),
                (0, 2.50, 4.50, 6.10, 7.50, 8.70, 9.75, 10.65, 11.40, 12.00, 12.45),
                (0, 2.00, 3.50, 4.70, 5.65, 6.40, 7.05, 7.60, 8.05, 8.40, 8.65),
                (0, 2.00, 3.25, 4.20, 4.95, 5.55, 6.05, 6.45, 6.75, 6.95, 7.05),
                (0, 0.85, 1.50, 2.00, 2.40, 2.75, 3.00, 3.20, 3.35, 3.45, 3.50)
            ),
            (
                (0, 2.30, 3.85, 5.10, 6.15, 7.05, 7.85, 8.55, 9.15, 9.65, 10.05),
                (0, 2.50, 4.80, 7.00, 9.00, 10.90, 12.60, 14.20, 15.60, 16.90, 18.00),
                (0, 2.80, 5.10, 7.00, 8.70, 10.20, 11.55, 12.75, 13.80, 14.70, 15.45),
                (0, 2.30, 4.10, 5.60, 6.85, 7.90, 8.85, 9.70, 10.45, 11.10, 11.65),
                (0, 2.30, 3.85, 5.10, 6.15, 7.05, 7.85, 8.55, 9.15, 9.65, 10.05),
                (0, 1.15, 2.10, 2.90, 3.60, 4.25, 4.80, 5.30, 5.75, 6.15, 6.50)
            )
        )
        self.AValueUp = []
        s = -1
        for i in self.AValues:
            s += 1
            r = -1
            rs = []
            for j in i:
                r += 1
                q = -1
                qs = []
                for k in j:
                    q += 1
                    if q + 1 < len(j):
                        qs.append(self.AValues[s][r][q + 1] - k)
                rs.append(qs)
            self.AValueUp.append(rs)

        # self.Provides = self.generate_4_dimensional_list()
        # self.MyCosts = self.generate_4_dimensional_list()
        # self.TentProfits = self.generate_4_dimensional_list()
        # self.Bids = self.generate_4_dimensional_list()
        # self.Asks = self.generate_4_dimensional_list()

        self.QReached = \
            [  # Initializing a three dimensional array [phase][period][group]
                4 * [
                    24 * [  # 24 Periods of Phase 1, 2, 3
                        self.group_size * [0]  # 6 groups
                    ]
                ]
            ]

        self.NotIntegers = [  # Initializing a two dimensional array [group][role]
            self.group_size * [  # 6 groups
                self.group_size * [False]  # 6 roles
            ]
        ]

    def generate_4_dimensional_list(self):
        return [  # Initializing a four dimensional list [phase, period, group, role]
            4 * [
                24 * [  # 24 Periods of Phase 1, 2, 3
                    self.group_size * [  # 6 groups
                        self.group_size * [0]  # 6 roles
                    ]
                ]
            ]
        ]


class Phase(object):
    """docstring for Phase"""
    def __init__(self, session, key):
        super(Phase, self).__init__()
        self.session = session
        session.phases[key] = self
        self.key = key
        self.periods = {}
        self.profits = {}
        self.balances = {}


class Period(object):
    """docstring for Period"""
    def __init__(self, phase, key):
        super(Period, self).__init__()
        self.phase = phase
        phase.periods[key] = self
        self.key = key
        self.groups = {}
        self.profits = {}
        self.balances = {}


class Group(object):
    """docstring for Group"""

    stages = {
        -1: '',
        0: 'input>0',
        1: 'provide calcs',
        2: 'init result',
        3: 'no aftermarket',
        4: 'stage 0',
        5: 'preDisplay',
        6: 'prep up',
        7: 'up ready',
        8: 'get AcceptBid',
        9: 'PreResultUp',
        10: 'Between Directions',
        11: 'PrepDn',
        12: 'ready Dn',
        13: 'get AcceptAsk',
        14: 'PreResultDn',
        15: 'Result'
    }

    def __init__(self, period, key):
        super(Group, self).__init__()
        self.period = period
        period.groups[key] = self
        self.key = key

        self.stage = -1
        self.stage_name = ''
        self.direction = 0
        self.quantity_initial = 0
        self.quantity_reached = 0
        self.quantity_up = 0
        self.quantity_down = 0

        self.bid_diff_up = 222
        self.bid_diff_down = 222
        self.up_covered = -2
        self.down_covered = -2

        self.sum_provides = 0
        self.sum_halvers = 0
        self.sum_bids = 0
        self.sum_asks = 0

        self.bids = None
        self.asks = None
        self.provides = None

        self.label_continue = 'Continue'

        self.coin_flip = 0
        self.outcome = 0


class Subject(object):
    """docstring for Subject"""

    states = {
        0: 'passive',
        1: 'initial',
        2: 'dropped',
        3: 'suspended',
        100: 'active',
        101: 'waiting',
        102: 'bankrupt',
        103: 'robot'
        }

    statuses = {
        0: '',
        1: 'live',
        2: 'losing',
        3: 'bankrupt',
        4: 'robot'
    }

    def __init__(self, session, key=None):
        super(Subject, self).__init__()
        self.session = session
        if key is None:
            key = str(uuid.uuid4())
        self.session.subjects[key] = self
        self.key = key
        self.session_key = key
        self.name = None
        self.previous_state = 1
        self.state = 1
        self.state_name = Subject.states[self.state]
        self.previous_status = 0
        self.status = 0
        self.is_suspended = False
        self.is_initialized = False
        self.group = None
        self.group_key = 0
        self.role = 0

        self.my_cost = 0
        self.tent_profit = 0
        self.profit = 0
        self.period_profits = [[0] * 24] * 4
        self.phase_profits = [0] * 4
        self.total_profit = 0
        self.aft_profit = 0
        self.current_balance = 0
        self.my_bid = -1
        self.my_ask = -1
        self.my_tax = -1
        self.my_rebate = -1
        self.price = 0

        self.example_cost = 0
        self.my_provide = None
        self.default_provide = 0

        self.time_left = 0
        self.is_participating = True

        self.value_up = 0
        self.value_down = 0

    @staticmethod
    def get_state_by_name(name):
        d = Subject.states
        return list(d.keys())[list(d.values()).index(name)]

    def set_state(self, name):
        self.previous_state = self.state
        self.state = self.get_state_by_name(name)
        self.state_name = name
        return self.state

    @staticmethod
    def get_status_by_name(name):
        d = Subject.statuses
        return list(d.keys())[list(d.values()).index(name)]

    def set_status(self, name):
        self.previous_status = self.status
        self.status = self.get_status_by_name(name)
        return self.status

    def decide_state(self):
        if not self.is_initialized and self.name is None:
            self.set_state('initial')
        else:
            self.is_initialized = True
            self.set_state('waiting')

    def restore_state(self):
        state = Subject.states[self.previous_state]
        self.set_state(state)

    def is_passive(self):
        return int(self.state / 100) == 0

    def is_active(self):
        return int(self.state / 100) == 1

    def to_dict(self):
        return dict(
            key=self.key,
            name=self.name,
            state=self.state,
            state_name=Subject.states[self.state],
            status=self.status,
            status_name=Subject.statuses[self.status],
            is_suspended=self.is_suspended,
            group=self.group,
            role=self.role,
            example_cost=self.example_cost,
            time_left=self.time_left,
            my_provide=self.my_provide,
            my_bid=self.my_bid,
            my_ask=self.my_ask,
            my_tax=self.my_tax,
            my_rebate=self.my_rebate,
            price=self.price
            )


class Experimenter(object):
    """docstring for Experimenter"""
    def __init__(self, session, key=None):
        super(Experimenter, self).__init__()
        self.session = session
        if key is None:
            key = str(uuid.uuid4())
        self.key = key


class Application(tornado.web.Application):
    """docstring for Application"""
    def __init__(self, public_path):
        self.subjects = {}
        self.experimenters = {}
        self.sessions = {}
        self.groups = {}
        self.sockets = {}
        self.public_path = public_path
        _handlers = [
            (r'/client', handlers.ClientHandler),
            (r'/server', handlers.ServerHandler),
            (r'/socket', handlers.SocketHandler),
            (r'/', tornado.web.RedirectHandler, dict(url="/client")),
            (
                r'/(.*)',
                tornado.web.StaticFileHandler,
                {'path': self.public_path}
            )
        ]
        settings = dict(
            xsrf_cookies=True,
            cookie_secret="4s0$3yt1tpr3s",
            debug=True
        )
        tornado.web.Application.__init__(self, _handlers, **settings)

    def get_socket(self, key):
        ss = self.sockets.values()
        return next((s for s in ss if s.key == key), None)

    def get_current_phase(self, session):
        return session.phases[session.phase]

    def get_current_period(self, session):
        phase = self.get_current_phase(session)
        return phase.periods[session.period]

    def get_group(self, session, group):
        period = self.get_current_period(session)
        if group in period.groups:
            return period.groups[group]
        else:
            return None

    def get_subject(self, key):
        ss = self.subjects.values()
        return next((s for s in ss if s.key == key or s.name == key), None)

    def get_subjects_by_state(self, state_name):
        state = Subject.get_state_by_name(state_name)
        ss = self.subjects.values()
        ss = list(s for s in ss if s.state == state)
        return ss

    def get_subjects_by_group(self, group):
        ss = self.subjects.values()
        ss = list(s for s in ss if s.group_key == group)
        return ss

    def get_subjects_by_active(self, session):
        ss = self.subjects.values()
        ss = list(s for s in ss if s.session == session and s.is_active())
        return ss

    def set_subject(self, subject):
        self.subjects[subject.key] = subject

    def get_experimenter(self, key):
        es = self.experimenters.values()
        return next((e for e in es if e.key == key), None)

    def set_experimenter(self, experimenter):
        self.experimenters[experimenter.key] = experimenter

    def start_session(self, session):
        session.is_started = True
        session.is_finished = False
        session.phase = 0
        self.start_phase(session)

    def stop_session(self, session):
        session.is_started = False
        session.is_finished = False
        session.phase = 0
        session.period = 0
        session.stage = 0

    def finish_session(self, session):
        session.is_finished = True

    def start_phase(self, session):
        ss = self.get_subjects_by_active(session)
        if session.phase > 0:
            phase = self.get_current_phase(session)
            for s in ss:
                phase.profits[s.key] = s.current_balance - phase.balances[s.key]
        phase = Phase(session, session.phase)
        for s in ss:
            phase.balances[s.key] = s.current_balance
        session.phases[session.phase] = phase
        session.period = 0
        self.start_period(session)

    def start_period(self, session):
        phase = session.phases[session.phase]
        period = Period(phase, session.period)
        roles = list(range(session.group_size))
        random.shuffle(roles)
        ss = self.subjects.values()
        ss = list(s for s in ss if s.session == session and s.is_active())
        random.shuffle(ss)
        group = 0
        for i, s in enumerate(ss):
            if i > 0 and i % session.group_size == 0:
                group += 1
            s.group_key = group
            if group not in period.groups:
                g = Group(period, group)
            s.group = period.groups[group]
            s.role = roles[i % session.group_size]
            s.period_profit = 0
            if session.phase == 0 and session.period == 1:
                s.total_profit = 0
                s.current_balance = session.starting_balance
            if session.period == 1:
                s.phase_profit = 0

        ps = session.AValuesParamSets[session.phase][session.period]
        if ps < 2:
            session.cost = session.cost_low
        else:
            session.cost = session.cost_high
        session.input_step_max = session.cost / session.input_step_size
        session.input_step_time = 3
        session.time_for_preparation = 3
        if session.period == 1:
            session.input_step_time = 5
            session.time_for_preparation = 5
            session.time_for_input = 100
            session.time_for_result = 125
        elif session.period == 2:
            session.time_for_input = 85
            session.time_for_result = 85
        else:
            session.time_for_input = 75
            session.time_for_result = 65

        for k, g in period.groups.items():
            if session.phase > 0:
                g.stage = 0
            else:
                g.stage = 4
            g.stage_name = Group.stages[g.stage]
            self.start_stage(session, k)

    def start_stage(self, session, group):
        gr = group
        period = self.get_current_period(session)
        g = period.groups[gr]
        g.label_continue = 'Continue'
        ph = session.phase
        pe = session.period
        ss = self.get_subjects_by_group(gr)
        ss = list(s for s in ss if s.session == session and s.is_active())
        for i, s in enumerate(ss):
            s.is_participating = True
            s.time_left = 0

        if g.stage == 0:
            for i, s in enumerate(ss):
                s.time_left = session.time_for_input
                s.example_cost = session.AValueUp[ph][s.role][2]
                defp = 0
                while session.AValueUp[ph][s.role][defp] > s.cost / 2:
                    defp += 1
                s.default_provide = defp
                s.my_provide = None
                s.time_left = session.time_for_input
        elif g.stage == 1:
            for i, s in enumerate(ss):  # Iterating over subjects
                if s.my_provide is None:
                    s.my_provide = s.default_provide
            g.provides = list(s.my_provide for s in ss)
            g.sum_provides = sum(g.provides)
            g.sum_halvers = len(s for s in ss if s.my_provide is not None and float(s.my_provide) - int(s.my_provide) > 0)
            g.quantity_reached = min(session.quantity_max, g.sum_provides)
            g.some_refund = 0
            if g.sum_halvers == 1 \
                or g.sum_halvers == 3 \
                    or g.sum_halvers == 5:
                g.some_refund = 1
            if (ph > 1):
                g.quantity_initial = g.quantity_reached
                g.quantity_up = s.quantity_initial + 1
                g.quantity_down = s.quantity_initial - 1
                g.direction = 0
                if g.quantity_down == -1:
                    g.direction = 1
                elif s.quantity_up == 11:
                    g.direction = -1
            for i, s in enumerate(ss):  # Iterating over subjects
                s.my_cost_unit = s.my_provide
                not_integer = float(s.my_provide) - int(s.my_provide) > 0
                if not_integer and g.some_refund == 1:
                    s.my_cost_unit = s.my_provide - 0.5 / g.sum_halvers
                s.my_cost = session.cost * s.my_cost_unit
                s.tent_profit = session.AValues[session.AValuesParamSets[ph][pe], s.role, g.quantity_reached] - s.my_cost
                s.profit = s.tent_profit
                s.total_profit += s.profit
                s.current_balance += s.profit
            return self.next_stage(session, group)
        elif g.stage == 2:
            for i, s in enumerate(ss):
                s.time_left = session.time_for_result
        elif g.stage == 3:
            if ph == 1 or pe % 2 != 0:
                for i, s in enumerate(ss):
                    if s.current_balance < -session.maximum_loss:
                        s.is_suspended = True
                        s.set_status('robot')
                    elif s.current_balance < 0:
                        s.set_status('losing')
                session.period += 1
                self.start_period(session)
            else:
                self.next_stage(session, group)
            return
        elif g.stage == 4:
            for i, s in enumerate(ss):
                if ph == 0:
                    g.quantity_initial = session.AInitQ[session.period]
                    g.direction = session.ADirectionPhase1[session.period]
                    g.quantity_up = g.quantity_initial + 1
                    g.quantity_down = g.quantity_initial - 1
                s.value_up = session.AValueUp[session.AValuesParamSets[ph][pe]][s.role][g.quantity_initial]
                s.value_down = session.AValueUp[session.AValuesParamSets[ph][pe]][s.role][g.quantity_down]
            g.stage = 5
        elif g.stage == 6:
            return self.next_stage(session, group)
        elif g.stage == 7:
            if g.direction == -1:
                return self.next_stage(session, group)
            for i, s in enumerate(ss):
                s.time_left = session.time_for_preparation
        elif g.stage == 8:
            if g.direction == -1:
                return self.next_stage(session, group)
            for i, s in enumerate(ss):
                s.my_bid = -1
                s.price = 0
                s.time_left = session.input_step_max * session.input_step_time
            g.label_continue = 'Accept'
        elif g.stage == 9:
            if g.direction == -1:
                return self.next_stage(session, group)
            default_bid = min(session.cost, self.roundup(s.value_up, 0.5))
            for i, s in enumerate(ss):
                s.time_left = 1
                if s.my_bid == -1:
                    s.my_bid = default_bid
                    s.time_left = 7
            g.bids = list(s.my_bid for s in ss)
            g.sum_bids = sum(g.bids)
            g.up_covered = 0
            if g.sum_bids >= session.cost:
                g.up_covered = 1
            return self.next_stage(session, group)
        elif g.stage == 10:
            if g.direction != 0:
                return self.next_stage(session, group)
            for i, s in enumerate(ss):
                s.time_left = session.time_for_preparation + 2
        elif g.stage == 11:
            return self.next_stage(session, group)
        elif g.stage == 12:
            if g.direction == 1:
                return self.next_stage(session, group)
            for i, s in enumerate(ss):
                s.time_left = session.time_for_preparation
        elif g.stage == 13:
            if g.direction == 1:
                return self.next_stage(session, group)
            for i, s in enumerate(ss):
                s.my_ask = -1
                s.price = 0
                s.time_left = session.input_step_max * session.input_step_time
            g.label_continue = 'Accept'
        elif g.stage == 14:
            if g.direction == 1:
                return self.next_stage(session, group)
            default_ask = session.cost
            for i, s in enumerate(ss):
                s.time_left = 1
                if s.my_ask == -1:
                    s.my_ask = default_ask
                    s.time_left = 7
            g.asks = list(s.my_ask for s in ss)
            g.sum_asks = sum(g.asks)
            g.down_covered = 0
            if g.sum_asks <= session.cost:
                g.down_covered = 1
            return self.next_stage(session, group)
        elif g.stage == 15:
            if g.direction == 0 and g.up_covered == 1 and g.down_covered == 1:  # Coin flip
                g.coin_flip = [-1, 1][random.randint(0, 1)]
                g.outcome = g.coin_flip
            elif g.up_covered == 1:
                g.outcome = 1
            elif g.down_covered == 1:
                g.outcome = -1
            else:
                g.outcome = 0
            for i, s in enumerate(ss):
                s.time_left = 30
                if session.period == 1:
                    s.time_left = 45
                if g.direction > -1:
                    s.my_tax = 0
                    if g.up_covered == 1:
                        s.my_tax = max(session.cost - (g.sum_bids - s.my_bid), 0)
                if g.direction < 1:
                    s.my_rebate = 0
                    if g.down_covered == 1:
                        s.my_rebate = session.cost - (g.sum_asks - s.my_ask)
                if g.outcome == 1:
                    s.aft_profit = s.value_up - s.my_tax
                elif g.outcome == -1:
                    s.aft_profit = s.my_rebate - s.value_down
                else:
                    s.aft_profit = 0
                s.profit = s.aft_profit
                if ph == 2 or pe % 2 == 0:
                    s.profit = s.tent_profit + s.aft_profit
                s.total_profit += s.aft_profit
        for i, s in enumerate(ss):
            s.set_state('active')
            socket = self.get_socket(s.key)
            if socket is not None:
                if s.time_left > 0:
                    socket.timer = threading.Timer(s.time_left, socket.input_timeout)
                    socket.timer.start()
                socket.send('continue_session', s)

    def next_stage(self, session, group):
        g = self.get_group(session, group)
        if g.stage < 15:
            g.stage += 1
            self.start_stage(session, group)

    def next_period(self, session):
        if (session.phase == 0 and session.period < 12) \
                or (session.phase > 0 and session.period < 24):
            session.period += 1
            self.start_period(session)
        else:
            self.next_phase(session)

    def next_phase(self, session):
        if session.phase < 3:
            session.phase += 1
            session.start_phase(session)
        else:
            self.finish_session(session)

    def proceed(self, session):
        period = self.get_current_period(session)
        waiting_groups = []
        finished_groups = []
        for (i, group) in period.groups.items():
            subjects = self.get_subjects_by_group(i)
            if len(list(s for s in subjects if Subject.states[s.state] == 'waiting')) == len(subjects):
                waiting_groups.append(group.key)
                if group.stage == 15:
                    finished_groups.append(group.key)
        if len(finished_groups) == len(period.groups):
            self.next_period(session)
        elif len(waiting_groups) > 0:
            for group in waiting_groups:
                self.next_stage(session, group)

    @staticmethod
    def roundup(x, y):
        h = y
        if x > y:
            for i in range(2, 100):
                z = i * round(y, 5)
                if x <= z:
                    return round(z, 5)
                    break
        if x < h:
            return round(h, 5)
        if x == h:
            return round(h, 5)