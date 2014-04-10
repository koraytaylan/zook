import zook
import tornado.websocket
import time
import simplejson as json
import uuid
import codecs
import os
import sys
import traceback
import logging


class ClientHandler(tornado.web.RequestHandler):
    """docstring for ClientHandler"""
    def get(self):
        path = os.path.join(self.application.public_path, 'client.html')
        with codecs.open(path, 'r', 'utf-8') as f:
            read_data = f.read()
        self.write(read_data)


class ServerHandler(tornado.web.RequestHandler):
    """docstring for ServerHandler"""
    def get(self):
        path = os.path.join(self.application.public_path, 'server.html')
        with codecs.open(path, 'r', 'utf-8') as f:
            read_data = f.read()
        self.write(read_data)


class SocketHandler(tornado.websocket.WebSocketHandler):
    """docstring for SocketHandler"""
    def open(self):
        self.session = self.find_session()
        self.key = str(uuid.uuid4())
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
        elif message_type == 'set_subject':
            return self.set_subject(o)
        elif message_type == 'get_subjects':
            return self.get_subjects(o)
        return self.send('invalid_operation', 'unknown message type', id)

    def serialize(self, message):
        o = json.dumps(message)
        return o

    def send(self, message_type='reply', message=None, id=None):
        m = dict(
            type=message_type,
            timestamp=int(time.time() * 1000),
            data=message
        )
        if id is not None:
            m['id'] = id
        self.write_message(self.serialize(m))

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
            key = uuid.UUID(data)
            return str(key)
        except:
            return None

    def init(self, message):
        data = {}
        subject = None
        try:
            if 'data' in message and message['data'] is not None:
                key = self.parse_key(message['data'])
                if key is not None:
                    ss = self.session.subjects
                    subject = next(
                        (s for s in ss.values() if s.key == key),
                        None
                        )
                    ss = self.application.sockets
                    for s in (s for s in ss.values() if s.key == key):
                        s.close()
                    del self.application.sockets[self.key]
                    self.key = key
                    self.application.sockets[self.key] = self
            data['key'] = self.key
            data['session'] = dict(
                key=str(self.session.key),
                is_started=self.session.is_started,
                is_finished=self.session.is_finished
                )
            self.is_initialized = True
            return self.send('initialize', data, message['id'])
        except:
            return self.send('internal_error', str(traceback.format_exc()))

    def find_subject(self, key):
        ss = self.session.subjects.values()
        return next((s for s in ss if s.key == key or s.name == key), None)

    def get_subject(self, message):
        subject = None
        key = None
        if self.is_experimenter:
            if 'data' not in message or message['data'] is None:
                return self.send(
                    'invalid_operation',
                    'key for the subject to be retrieved' +
                    ' should be defined in "data"'
                    )
            key = message['data']
        else:
            key = self.key
        subject = self.find_subject(key)
        o = None
        if subject is not None:
            o = subject.to_dict()
        return self.send('get_subject', o, message['id'])

    def get_subjects(self, message):
        if not self.is_experimenter:
            return self.send(
                'invalid_operation',
                'access denied'
                )
        ss = []
        for s in self.subjects.values():
            ss.append(s.to_dict())
        return self.send('get_subjects', ss, message['id'])

    def set_subject(self, message):
        if 'data' not in message or message['data'] is None:
            return self.send(
                'invalid_operation',
                'message should contain a "data"'
                )
        data = message['data']
        subject = None
        key = None
        if self.is_experimenter:
            if 'key' not in data or message['key'] is None:
                return self.send(
                    'invalid_operation',
                    'key for the subject to be modified' +
                    ' should be defined in "data.key"'
                    )
            key = data['key']
        else:
            key = self.key
        subject = self.find_subject(key)
        if subject is None:
            subject = zook.Subject(self.session, key)
        if 'name' in data:
            name = data['name']
            if not name or not name.strip():
                return self.send(
                    'invalid_operation',
                    'Client name can not be empty'
                    )
            s = self.find_subject(name)
            if s is not None:
                return self.send(
                    'invalid_operation',
                    'There already is another' +
                    ' client named with "{0}"'.format(name),
                    message['id']
                    )
            subject.name = name
        elif not subject.name:
            return self.send(
                'invalid_operation',
                'Client name can not be empty',
                message['id']
                )
        return self.send('set_subject', subject.to_dict(), message['id'])