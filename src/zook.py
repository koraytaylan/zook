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


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    """docstring for EchoWebSocket"""
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message("You said: " + message)

    def on_close(self):
        print("WebSocket closed")


class SocketHandler(tornado.websocket.WebSocketHandler):
    """docstring for SocketHandler"""
    def open(self):
        self.subject = None
        self.key = uuid.uuid4()
        sockets[self.key] = self
        self.is_initialized = False

    def on_close(self):
        del sockets[self.key]

    def on_message(self, message):
        o = None
        id = None
        message_type = None
        try:
            o = json.loads(message)
        except:
            return self.send('invalid_message', 'message should be in json format')
        if 'id' not in o:
            return self.send('invalid_message', 'message should contain an "id"', id)
        else:
            id = o['id']
        if 'type' not in o:
            return self.send('invalid_message', 'message should contain a "type"', id)
        else:
            message_type = o['type']
        if self.is_initialized is False and message_type != 'initialize':
            return self.send('not_initialized', 'socket service should be initialized first before sending/receiving messages', id)
        elif message_type == 'initialize':
            return self.init(o)
        return self.send('invalid_message', 'unknown message type', id)

    def send(self, message_type='reply', message=None, id=None):
        m = dict(
            type=message_type,
            timestamp=int(time.time() * 1000),
            data=message
        )
        if id is not None:
            m['id'] = id
        self.write_message(json.dumps(m))

    def init(self, message):
        try:
            key = uuid.UUID(message['data'])
            if key in sockets:
                socket = sockets[key]
                if socket is not self:
                    self.subject = socket.subject
                    socket.close()
            else:
                del sockets[self.key]
            self.key = key
            sockets[self.key] = self
            self.is_initialized = True
            return self.send('initialize', str(self.key), message['id'])
        except:
            return self.send('invalid_message')

    def get_subject(self, message):
        return self.send('get_subject', self.subject, message['id'])


class Application(tornado.web.Application):
    """docstring for Application"""
    def __init__(self):
        handlers = [
            #(r'/', tornado.web.RedirectHandler, {'url': '/index.html'})
            (r'/socket', SocketHandler),
            (r'/echo', EchoWebSocket),
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