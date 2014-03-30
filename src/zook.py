import tornado.web
import os
import handlers


class Session(object):
    """docstring for Session"""
    def __init__(self):
        super(Session, self).__init__()
        self.subjects = {}
        self.phases = {}
        self.groups = {}
        self.current_phase = 0
        self.is_started = False
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
    def __init__(self, session, name):
        super(Subject, self).__init__()
        self.session = session
        self.name = name
        session.subjects[name] = self


class Application(tornado.web.Application):
    """docstring for Application"""
    def __init__(self):
        self.public_path = os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)
                ),
            os.path.pardir,
            'public'
            )
        _handlers = [
            (r'/socket', handlers.SocketHandler),
            (r'/', handlers.MainHandler),
            (
                r'/(.*)',
                tornado.web.StaticFileHandler,
                {'path': self.public_path}
            )
        ]
        settings = dict(
            template_path=self.public_path,
            static_path=self.public_path,
            # static_url_prefix = "/",
            xsrf_cookies=True,
            cookie_secret="4s0$3yt1tpr3s",
            # login_url="/auth/login",
            debug=True
        )
        tornado.web.Application.__init__(self, _handlers, **settings)
        self.sessions = {}
        self.sockets = {}