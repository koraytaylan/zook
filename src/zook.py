import tornado.web
import uuid
import random
import threading
import handlers
import os
import json
import time


def roundup(x, y):
    h = y
    if x > y:
        for i in range(2, 100):
            z = i * round(y, 5)
            if x <= z:
                return round(z, 5)
    if x < h:
        return round(h, 5)
    if x == h:
        return round(h, 5)


class Session(object):
    """docstring for Session"""

    def __init__(self):
        super(Session, self).__init__()
        self.created_at = time.time()
        self.key = str(uuid.uuid4())
        self.subjects = {}
        self.experimenters = {}
        self.phases = {}
        self.phase = None
        self.period = None
        self.is_started = False
        self.is_finished = False
        self.is_all_ready = False

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

    def start(self):
        self.is_started = True
        self.is_finished = False
        for (i, s) in self.subjects.items():
            s.set_state('active')
        self.phase = Phase(self, 0)
        self.phase.start()

    def stop(self):
        self.is_started = False
        self.is_finished = False
        self.phase = None
        self.period = None
        for (i, s) in self.subjects.items():
            s.set_state('waiting')

    def finish(self):
        self.is_finished = True

    def get_subjects_by_active(self):
        ss = self.subjects.values()
        ss = list(s for s in ss if s.session == self and s.is_active())
        return ss

    def get_subjects_by_group(self, group):
        ss = self.subjects.values()
        ss = list(s for s in ss if s.group == group)
        return ss

    def next_phase(self):
        if self.phase is not None:
            self.phase.finish()
        if self.phase.key < 3:
            p = Phase(self, self.phase.key + 1)
            p.start()
        else:
            self.finish()


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
        self.is_skipped = False

    def start(self):
        ss = self.session.get_subjects_by_active()
        for s in ss:
            self.balances[s.key] = s.current_balance
            self.phase_profit = 0
            if self.key == 0:
                s.total_profit = 0
                s.current_balance = self.session.starting_balance
        self.session.phase = self
        p = Period(self, 0)
        p.start()

    def finish(self):
        ss = self.session.get_subjects_by_active()
        for s in ss:
            self.profits[s.key] = s.current_balance - self.balances[s.key]

    def next_period(self):
        if self.session.period is not None:
            self.session.period.finish()
        if self.is_skipped:
            self.session.next_phase()
        elif (self.session.phase.key == 0 and self.session.period.key < 12) \
                or (self.session.phase.key > 0 and self.session.period.key < 24):
            p = Period(self, self.session.period.key + 1)
            p.start()
        else:
            self.session.next_phase()


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
        self.cost = 0

    def start(self):
        session = self.phase.session
        ss = session.get_subjects_by_active()
        roles = list(range(session.group_size))
        random.shuffle(roles)
        random.shuffle(ss)
        group = 0
        for i, s in enumerate(ss):
            self.balances[s.key] = s.current_balance
            if i > 0 and i % session.group_size == 0:
                group += 1
            if group not in self.groups:
                g = Group(self, group)
            s.group = self.groups[group]
            s.role = roles[i % session.group_size]
            g.subjects[s.key] = s
            g.roles[s.key] = s.role
            s.period_profit = 0

        ps = session.AValuesParamSets[self.phase.key][self.key]
        if ps < 2:
            self.cost = session.cost_low
        else:
            self.cost = session.cost_high
        session.input_step_max = self.cost / session.input_step_size
        session.input_step_time = 1
        session.time_for_preparation = 3
        if self.key == 1:
            session.input_step_time = 5
            session.time_for_preparation = 5
            session.time_for_input = 100
            session.time_for_result = 125
        elif self.key == 2:
            session.time_for_input = 85
            session.time_for_result = 85
        else:
            session.time_for_input = 75
            session.time_for_result = 65

        session.period = self
        for k, g in self.groups.items():
            if self.phase.key > 0:
                g.stage = 0
            else:
                g.stage = 4
            g.start_stage()

    def finish(self):
        ss = self.phase.session.get_subjects_by_active()
        for s in ss:
            self.profits[s.key] = s.current_balance - self.balances[s.key]


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
        self.subjects = {}
        self.roles = {}

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

        self.bids = {}
        self.asks = {}
        self.provides = {}

        self.label_continue = 'Continue'

        self.coin_flip = 0
        self.outcome = 0

        self.is_finished_period = False

    def set_stage(self, stage):
        self.stage = stage
        self.stage_name = Group.stages[stage]

    def next_stage(self):
        if (self.stage < 15):
            self.stage += 1
        self.start_stage()

    def start_stage(self):
        group = self
        period = self.period
        phase = period.phase
        session = phase.session
        group.stage_name = Group.stages[group.stage]
        group.label_continue = 'Continue'
        ph = phase.key
        pe = period.key
        param_set = session.AValuesParamSets[ph][pe]
        ss = session.get_subjects_by_group(group)
        ss = list(s for s in ss if s.session == session and s.is_active())
        for i, s in enumerate(ss):
            s.is_participating = True
            s.time_left = 0
            s.set_state('active')

        if group.stage == 0:
            for i, s in enumerate(ss):
                s.time_left = session.time_for_input
                s.example_cost = session.AValueUp[ph][s.role][2]
                defp = 0
                while session.AValueUp[ph][s.role][defp] > period.cost / 2:
                    defp += 1
                s.default_provide = defp
                s.my_provide = None
                s.time_left = session.time_for_input
        elif group.stage == 1:
            for i, s in enumerate(ss):  # Iterating over subjects
                if s.is_robot:
                    sp = 0.5
                    rp = 0
                    while True:
                        rpIn = rp
                        if session.AValueUp[param_set][s.role][rp + 1] > period.cost / 2:
                            rp += sp
                        if rpIn == rp:
                            break
                        rpIn = rp
                        if session.AValueUp[param_set][s.role][rp + 0.5] > period.cost:
                            rp += sp
                        if rpIn == rp:
                            break
                    s.my_provide = rp
                elif s.my_provide is None:
                    s.my_provide = s.default_provide
                group.provides[s.key] = float(s.my_provide)
                group.sum_provides += float(s.my_provide)
            group.sum_halvers = len(
                list(s for s in ss if s.my_provide is not None and float(s.my_provide) - float(s.my_provide) > 0)
            )
            group.quantity_reached = min(session.quantity_max, int(group.sum_provides))
            group.some_refund = 0
            if group.sum_halvers == 1 \
                or group.sum_halvers == 3 \
                    or group.sum_halvers == 5:
                group.some_refund = 1
            if (ph > 1):
                group.quantity_initial = group.quantity_reached
                group.quantity_up = group.quantity_initial + 1
                group.quantity_down = group.quantity_initial - 1
                group.direction = 0
                if group.quantity_down == -1:
                    group.direction = 1
                elif group.quantity_up == 11:
                    group.direction = -1
            for i, s in enumerate(ss):  # Iterating over subjects
                s.my_cost_unit = float(s.my_provide)
                not_integer = float(s.my_provide) - float(s.my_provide) > 0
                if not_integer and group.some_refund == 1:
                    s.my_cost_unit = s.my_provide - 0.5 / group.sum_halvers
                s.my_cost = period.cost * s.my_cost_unit
                param = session.AValuesParamSets[ph][pe]
                s.tent_profit = session.AValues[param][s.role][group.quantity_reached] - s.my_cost
                s.period_profit = s.tent_profit
                s.total_profit += s.period_profit
                s.current_balance += s.period_profit
            return self.next_stage()
        elif group.stage == 2:
            for i, s in enumerate(ss):
                s.time_left = session.time_for_result
            if ph == 1 or pe % 2 != 0:
                for i, s in enumerate(ss):
                    if s.current_balance < -session.maximum_loss:
                        s.is_robot = True
                        s.set_state('robot')
                group.is_finished_period = True
        elif group.stage == 3:
            return self.next_stage()
        elif group.stage == 4:
            for i, s in enumerate(ss):
                if ph == 0:
                    group.quantity_initial = session.AInitQ[pe]
                    group.direction = session.ADirectionPhase1[pe]
                    group.quantity_up = group.quantity_initial + 1
                    group.quantity_down = group.quantity_initial - 1
                s.value_up = session.AValueUp[session.AValuesParamSets[ph][pe]][s.role][group.quantity_initial]
                s.value_down = session.AValueUp[session.AValuesParamSets[ph][pe]][s.role][group.quantity_down]
            group.stage = 5
        elif group.stage == 6:
            return self.next_stage()
        elif group.stage == 7:
            if group.direction == -1:
                return self.next_stage()
            for i, s in enumerate(ss):
                s.time_left = session.time_for_preparation
        elif group.stage == 8:
            if group.direction == -1:
                return self.next_stage()
            for i, s in enumerate(ss):
                s.my_bid = -1
                s.time_left = session.input_step_max * session.input_step_time
            group.label_continue = 'Accept'
        elif group.stage == 9:
            if group.direction == -1:
                return self.next_stage()
            for i, s in enumerate(ss):
                default_bid = min(period.cost, roundup(s.value_up, 0.5))
                s.time_left = 1
                if s.is_robot:
                    s.my_bid = s.value_up
                elif s.my_bid == -1:
                    s.my_bid = default_bid
                    s.time_left = 7
                group.bids[s.key] = float(s.my_bid)
                group.sum_bids += float(s.my_bid)
            group.up_covered = 0
            if group.sum_bids >= period.cost:
                group.up_covered = 1
            return self.next_stage()
        elif group.stage == 10:
            if group.direction != 0:
                return self.next_stage()
            for i, s in enumerate(ss):
                s.time_left = session.time_for_preparation + 2
        elif group.stage == 11:
            return self.next_stage()
        elif group.stage == 12:
            if group.direction == 1:
                return self.next_stage()
            for i, s in enumerate(ss):
                s.time_left = session.time_for_preparation
        elif group.stage == 13:
            if group.direction == 1:
                return self.next_stage()
            for i, s in enumerate(ss):
                s.my_ask = -1
                s.time_left = session.input_step_max * session.input_step_time
            group.label_continue = 'Accept'
        elif group.stage == 14:
            if group.direction == 1:
                return self.next_stage()
            default_ask = period.cost
            for i, s in enumerate(ss):
                s.time_left = 1
                if s.is_robot:
                    s.my_ask = s.value_down
                elif s.my_ask == -1:
                    s.my_ask = default_ask
                    s.time_left = 7
                group.asks[s.key] = float(s.my_ask)
                group.sum_asks += float(s.my_ask)
            group.down_covered = 0
            if group.sum_asks <= period.cost:
                group.down_covered = 1
            return self.next_stage()
        elif group.stage == 15:
            if group.direction == 0 and group.up_covered == 1 and group.down_covered == 1:  # Coin flip
                group.coin_flip = [-1, 1][random.randint(0, 1)]
                group.outcome = group.coin_flip
            elif group.up_covered == 1:
                group.outcome = 1
            elif group.down_covered == 1:
                group.outcome = -1
            else:
                group.outcome = 0
            group.is_finished_period = True
            for i, s in enumerate(ss):
                s.time_left = 30
                if pe == 1:
                    s.time_left = 45
                if group.direction > -1:
                    s.my_tax = 0
                    if group.up_covered == 1:
                        s.my_tax = max(period.cost - (group.sum_bids - s.my_bid), 0)
                if group.direction < 1:
                    s.my_rebate = 0
                    if group.down_covered == 1:
                        s.my_rebate = period.cost - (group.sum_asks - s.my_ask)
                if group.outcome == 1:
                    s.aft_profit = s.value_up - s.my_tax
                elif group.outcome == -1:
                    s.aft_profit = s.my_rebate - s.value_down
                else:
                    s.aft_profit = 0
                s.period_profit = s.aft_profit
                if ph == 2 or pe % 2 == 0:
                    s.period_profit = s.tent_profit + s.aft_profit
                s.total_profit += s.aft_profit
                s.current_balance += s.period_profit
                if s.current_balance < -session.maximum_loss:
                    s.is_robot = True
                    s.set_state('robot')


class Subject(object):
    """docstring for Subject"""

    states = {
        0: 'passive',
        1: 'initial',
        2: 'dropped',
        3: 'suspended',
        100: 'active',
        101: 'waiting',
        102: 'robot'
        }

    def __init__(self, session, key=None):
        super(Subject, self).__init__()
        self.session = session
        if key is None:
            key = str(uuid.uuid4())
        self.session.subjects[key] = self
        self.key = key
        self.name = None
        self.previous_state = 1
        self.state = 1
        self.state_name = Subject.states[self.state]
        self.previous_status = 0
        self.status = 0
        self.is_suspended = False
        self.is_robot = False
        self.is_initialized = False
        self.group = None
        self.role = 0

        self.my_cost = 0
        self.tent_profit = 0
        self.period_profit = 0
        self.phase_profit = 0
        self.total_profit = 0
        self.aft_profit = 0
        self.current_balance = 0
        self.my_bid = -1
        self.my_ask = -1
        self.my_tax = -1
        self.my_rebate = -1

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
        if self.is_suspended:
            name = 'suspended'
        elif self.is_robot:
            name = 'robot'
        self.previous_state = self.state
        self.state = self.get_state_by_name(name)
        self.state_name = name
        return self.state

    def decide_state(self):
        if self.is_suspended:
            self.set_state('suspended')
        elif self.is_robot:
            self.set_state('robot')
        elif not self.is_initialized and self.name is None:
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

    def add_balance(self, amount):
        self.current_balance += amount
        self.phase_profit += amount
        self.period_profit += amount
        self.total_profit += amount


class Experimenter(object):
    """docstring for Experimenter"""
    def __init__(self, session, key=None):
        super(Experimenter, self).__init__()
        self.session = session
        if key is None:
            key = str(uuid.uuid4())
        self.key = key
        self.session.experimenters[key] = self


class Application(tornado.web.Application):
    """docstring for Application"""
    def __init__(self, public_path, data_path):
        self.subjects = {}
        self.experimenters = {}
        self.sessions = {}
        self.groups = {}
        self.sockets = {}
        self.public_path = public_path
        self.data_path = data_path
        _handlers = [
            (r'/client', handlers.ClientHandler),
            (r'/server', handlers.ServerHandler),
            (r'/socket', handlers.SocketHandler),
            (r'/export', handlers.ExportHandler),
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
        return session.phase

    def get_current_period(self, session):
        return session.period

    def get_group(self, session, group):
        if group in session.period.groups:
            return session.period.groups[group]
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

    def set_subject(self, subject):
        self.subjects[subject.key] = subject

    def get_experimenter(self, key):
        es = self.experimenters.values()
        return next((e for e in es if e.key == key), None)

    def set_experimenter(self, experimenter):
        self.experimenters[experimenter.key] = experimenter

    def start_session(self, session):
        session.start()
        self.continue_session(session)

    def stop_session(self, session):
        session.stop()
        self.continue_session(session)

    def continue_session(self, session, group=None):
        ss = session.get_subjects_by_active()
        if group is not None:
            ss = session.get_subjects_by_group(group)
        for i, s in enumerate(ss):
            socket = self.get_socket(s.key)
            if socket is not None:
                if s.time_left > 0:
                    socket.timer = threading.Timer(s.time_left, socket.input_timeout)
                    socket.timer.start()
                socket.send('continue_session', s)
        for i, e in session.experimenters.items():
            socket = self.get_socket(e.key)
            if socket is not None:
                socket.send('get_session', session)

    def proceed(self, session):
        period = self.get_current_period(session)
        waiting_groups = []
        finished_groups = []
        for (i, group) in period.groups.items():
            subjects = session.get_subjects_by_group(group)
            subjects = list(s for s in subjects if not s.is_suspended and not s.is_robot)
            subjects_waiting = list(s for s in subjects if Subject.states[s.state] == 'waiting')
            if len(subjects_waiting) == len(subjects):
                if group.is_finished_period:
                    finished_groups.append(group)
                else:
                    waiting_groups.append(group)
        if len(finished_groups) == len(period.groups):
            session.phase.next_period()
            self.write_to_file(session)
            self.continue_session(session)
        elif len(waiting_groups) > 0:
            for group in waiting_groups:
                group.next_stage()
                self.continue_session(session, group)

    @staticmethod
    def to_dict(obj, classkey=None, ignores=None):
        igs = []
        if ignores is not None:
            if obj in ignores:
                return None
            igs.extend(ignores)
        if hasattr(obj, '__dict__') and obj not in igs:
            igs.append(obj)
        if isinstance(obj, dict):
            data = {}
            for (k, v) in obj.items():
                data[k] = Application.to_dict(v, classkey, igs)
            return data
        elif isinstance(obj, list):
            data = []
            for v in obj:
                data.append(Application.to_dict(v, classkey, igs))
            return data
        elif hasattr(obj, "_ast"):
            return Application.to_dict(obj._ast())
        elif hasattr(obj, "__dict__"):
            data = dict([(key, Application.to_dict(value, classkey, igs))
                        for key, value in obj.__dict__.items()
                        if not callable(value) and not key.startswith('_')])
            if classkey is not None and hasattr(obj, "__class__"):
                data[classkey] = obj.__class__.__name__
            return data
        else:
            return obj

    def write_to_file(self, session):
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        with open(os.path.join(self.data_path, 'session-' + session.key + '.json'), 'w') as f:
            d = self.to_dict(session)
            j = json.dumps(d, sort_keys=True)
            f.write(j)
