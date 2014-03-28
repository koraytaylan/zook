import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import tornado.httpserver
import json
import uuid
import os
import codecs
import datetime, time
from handlers import *

public_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir, 'public')
sockets = {}


class Session(object):
    """docstring for Session"""
    def __init__(self):
        super(Session, self).__init__()
        self.phases = {}
        self.current_phase = 0
        self.current_period = 0


class Phase(object):
    """docstring for Phase"""
    def __init__(self, session, number):
        super(Phase, self).__init__()
        self.session = session
        self.number = number
        self.periods = {}


class Period(object):
    """docstring for Period"""
    def __init__(self, phase, number):
        super(Period, self).__init__()
        self.phase = phase
        self.number = number
        self.phase.periods[number] = self


class Subject(object):
    """docstring for Subject"""
    def __init__(self, session, name):
        super(Subject, self).__init__()
        self.session = session
        self.name = name


class MainHandler(tornado.web.RequestHandler):
    """docstring for MainHandler"""
    def get(self):
        key = self.get_secure_cookie('key')
        if key is None:
            self.set_secure_cookie('key', str(uuid.uuid4()))
        path = os.path.join(public_path, 'index.html')
        with codecs.open(path, 'r', 'utf-8') as f:
            read_data = f.read()
        self.write(read_data)

class Application(tornado.web.Application):
    """docstring for Application"""
    def __init__(self):
        handlers = [
            #(r'/', tornado.web.RedirectHandler, {'url': '/index.html'})
            (r'/socket', SocketHandler),
            (r'/', MainHandler),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': public_path}),
        ]
        settings = dict(
            blog_title="Zook",
            template_path=public_path,
            static_path=public_path,
            #static_url_prefix = "/",
            xsrf_cookies=True,
            cookie_secret="4s0$3yt1tpr3s",
            #login_url="/auth/login",
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)