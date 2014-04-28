import tornado.web
import os
import handlers
import uuid


class Session(object):
    """docstring for Session"""
    def __init__(self):
        super(Session, self).__init__()
        self.key = str(uuid.uuid4())
        self.phases = {}
        self.groups = {}
        self.current_phase = 0
        self.is_started = False
        self.is_finished = False
        self.group_size = 6
        self.starting_balance = 5

    def start(self):
        for s in (s for s in self.subjects.values() if s.is_active):
            s.total_profit = 0
            s.current_balance = self.starting_balance
            s.profit = 0
        self.is_started = True
        self.is_finished = False


class Phase(object):
    """docstring for Phase"""
    def __init__(self, session, number):
        super(Phase, self).__init__()
        self.session = session
        self.number = number
        self.periods = {}
        self.current_period = 0


class Period(object):
    """docstring for Period"""
    def __init__(self, phase, number):
        super(Period, self).__init__()
        self.phase = phase
        self.number = number
        self.phase.periods[number] = self


class Group(object):
    """docstring for Group"""
    def __init__(self, session):
        super(Group, self).__init__()
        self.session = session
        self.subjects = {}


class Subject(object):
    """docstring for Subject"""
    def __init__(self, session, key=None):
        super(Subject, self).__init__()
        self.session = session
        if key is None:
            key = str(uuid.uuid4())
        self.key = key
        self.name = None
        self.status = 'passive'
        self.total_profit = 0
        self.current_balance = session.starting_balance
        self.profit = 0
        self.bid_diff_up = 222
        self.bid_diff_down = 222
        self.up_covered = -2
        self.down_covered = -2
        self.my_bid = -1
        self.my_ask = -1

    def to_dict(self):
        return dict(
            key=self.key,
            name=self.name,
            status=self.status
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
        self.sessions = {}
        self.sockets = {}

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
        