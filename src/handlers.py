import zook
import tornado.websocket
import time
import json
import uuid
import codecs
import os
import sys
import traceback


class MainHandler(tornado.web.RequestHandler):
    """docstring for MainHandler"""
    def get(self):
        key = self.get_secure_cookie('key')
        if key is None:
            self.set_secure_cookie('key', str(uuid.uuid4()))
        path = os.path.join(self.application.public_path, 'index.html')
        with codecs.open(path, 'r', 'utf-8') as f:
            read_data = f.read()
        self.write(read_data)


class SocketHandler(tornado.websocket.WebSocketHandler):
    """docstring for SocketHandler"""
    def open(self):
        self.session = self.find_session()
        self.subject = None
        self.key = uuid.uuid4()
        self.application.sockets[self.key] = self
        self.is_initialized = False
        self.is_experimenter = False

    def on_close(self):
        if hasattr(self, 'key'):
            del self.application.sockets[self.key]

    def on_message(self, message):
        o = None
        id = None
        message_type = None
        try:
            o = json.loads(message)
        except:
            return self.send(
                'invalid_message',
                'message should be in json format'
                )
        if 'id' not in o:
            return self.send(
                'invalid_message',
                'message should contain an "id"',
                id
                )
        else:
            id = o['id']
        if 'type' not in o:
            return self.send(
                'invalid_message',
                'message should contain a "type"',
                id
                )
        else:
            message_type = o['type']
        if self.is_initialized is False and message_type != 'initialize':
            return self.send(
                'invalid_operation',
                'socket should be initialized first before sending messages',
                id
                )
        elif message_type == 'initialize':
            return self.init(o)
        elif message_type == 'get_subject':
            return self.get_subject(o)
        return self.send('invalid_operation', 'unknown message type', id)

    def send(self, message_type='reply', message=None, id=None):
        m = dict(
            type=message_type,
            timestamp=int(time.time() * 1000),
            data=message
        )
        if id is not None:
            m['id'] = id
        self.write_message(json.dumps(m))

    def find_session(self):
        session = None
        if len(self.application.sessions) > 0:
            session = next(
                (s for s in self.application.sessions.values()
                    if s.is_started is False),
                None
                )
        if session is None:
            session = zook.Session()
            self.application.sessions[session.key] = session
        return session

    def parse_key(self, data):
        try:
            return uuid.UUID(data)
        except:
            return None

    def init(self, message):
        data = {}
        try:
            if 'data' in message and message['data'] is not None:
                key = self.parse_key(message['data'])
                if key is not None and key in self.application.sockets:
                    socket = self.application.sockets[key]
                    if socket is not self:
                        self.subject = socket.subject
                        socket.close()
                    del self.application.sockets[self.key]
                    self.key = key
                    self.application.sockets[self.key] = self
            data['key'] = str(self.key)
            data['session'] = dict(
                key=str(self.session.key),
                is_started=self.session.is_started,
                is_finished=self.session.is_finished
                )
            self.is_initialized = True
            return self.send('initialize', data, message['id'])
        except:
            return self.send('internal_error', str(traceback.format_exc()))

    def get_subject(self, message):
        session = self.subject
        if self.is_experimenter:
            if 'data' not in message or message['data'] is None:
                return self.send(
                    'invalid_operation',
                    'key for the subject to be retrieved' +
                    ' should be defined in "data"'
                    )
            session = next(
                (s for s in self.session.subjects if s.key == message['data']),
                None
                )
        return self.send('get_subject', session, message['id'])

    def set_subject(self, message):
        if 'data' not in message or message['data'] is None:
            return self.send(
                'invalid_operation',
                'message should contain a "data"'
                )
        data = message['data']
        subject = None
        if self.is_experimenter:
            if 'key' not in data or message['key'] is None:
                return self.send(
                    'invalid_operation',
                    'key for the subject to be modified' +
                    ' should be defined in "data.key"'
                    )
            subject = next(
                (s for s in self.session.subjects if s.key == data['key']),
                None
                )
        if subject is not None:
            if 'name' in data:
                subject.name = data['name']
        return self.send('set_subject', subject, message['id'])