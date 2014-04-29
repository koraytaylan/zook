import tornado.web
import os
import handlers
import uuid
import random


class Session(object):
    """docstring for Session"""
    def __init__(self):
        super(Session, self).__init__()
        self.key = str(uuid.uuid4())
        self.phases = {}
        self.groups = {}
        self.current_phase = -1
        self.is_started = False
        self.is_finished = False

        self.cost_low = 3.0
        self.cost_high = 5.5
        self.quantity_max = 10  # Maximum feasible quantity
        self.input_min = 0
        self.input_max = 4

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
        r = -1
        q = -1
        for i in self.AValues:
            s += 1
            rs = []
            for j in i:
                r += 1
                qs = []
                for k in j:
                    q += 1
                    qs.append(self.AValues[s][r][q + 1] - k)
                rs.append(qs)
            self.AValueUp.append(rs)


class Phase(object):
    """docstring for Phase"""
    def __init__(self, session, number):
        super(Phase, self).__init__()
        self.session = session
        self.number = number
        self.periods = {}
        self.current_period = -1


class Period(object):
    """docstring for Period"""
    def __init__(self, phase, number):
        super(Period, self).__init__()
        self.phase = phase
        self.number = number
        self.phase.periods[number] = self


class Group(object):
    """docstring for Group"""
    def __init__(self, session, name):
        super(Group, self).__init__()
        self.session = session
        self.name = name


class Subject(object):
    """docstring for Subject"""

    states = {
        0: 'passive',
        1: 'initial',
        2: 'dropped',
        100: 'active',
        101: 'waiting'
        }

    def __init__(self, session, key=None):
        super(Subject, self).__init__()
        self.session = session
        if key is None:
            key = str(uuid.uuid4())
        self.key = key
        self.name = None
        self.previous_state = 1
        self.state = 1
        self.is_suspended = False
        self.is_initialized = False

        self.group = 0

        self.total_profit = 0
        self.current_balance = session.starting_balance
        self.profit = 0
        self.bid_diff_up = 222
        self.bid_diff_down = 222
        self.up_covered = -2
        self.down_covered = -2
        self.my_bid = -1
        self.my_ask = -1

    def set_state(self, state):
        d = Subject.states
        self.previous_state = self.state
        self.state = list(d.keys())[list(d.values()).index(state)]
        return self.state

    def decide_state(self):
        if not self.is_initialized and self.name is None:
            self.set_state('initial')
        else:
            self.is_initialized = True
            self.set_state('waiting')

    def restore_state(self):
        self.state = self.previous_state

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
            is_suspended=self.is_suspended
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

    def get_subject(self, key):
        ss = self.subjects.values()
        return next((s for s in ss if s.key == key or s.name == key), None)

    def set_subject(self, subject):
        self.subjects[subject.key] = subject

    def get_experimenter(self, key):
        es = self.experimenters.values()
        return next((e for e in es if e.key == key), None)

    def set_experimenter(self, experimenter):
        self.experimenters[experimenter.key] = experimenter

    def start_session(self, session):
        roles = list(range(0, 6))
        random.shuffle(roles)
        ss = self.subjects.values()
        ss = (s for s in ss if s.session == session and s.is_active())
        random.shuffle(ss)
        group = 0
        for i, s in enumerate(ss):
            if i % session.group_size == 0:
                group += 1
            s.group = group
            s.role = roles[i % session.group_size]
            s.total_profit = 0
            s.current_balance = self.starting_balance
            s.profit = 0
        self.is_started = True
        self.is_finished = False

    def roundup(x, y):
        h = y
        if x > y:
            for i in range(2, 100):
                z = i*round(y, 5)
                if x <= z:
                    return round(z, 5)
                    break
        if x < h:
            return round(h, 5)
        if x == h:
            return round(h, 5)

    def rounddown(x, y):
        if roundup(x, y) == x:
            return x
        else:
            return x - y