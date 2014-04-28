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


class InvalidOperationException(Exception):
    pass


class UnauthorizedOperationException(Exception):
    pass


class InvalidMessageException(Exception):
    pass


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
            s = self.application.get_subject(self.key)
            if s is not None:
                s.status = 'dropped'
                self.notify('set_subject', s.to_dict())

    def on_message(self, message):
        o = None
        id = None
        message_type = None
        reply = None
        try:
            try:
                o = json.loads(message)
            except:
                raise InvalidMessageException(
                    'Message should be in json format')
            if 'id' not in o:
                raise InvalidMessageException(
                    'Message should contain "id"')
            id = o['id']
            if 'type' not in o:
                raise InvalidMessageException(
                    'Message should contain "type"')
            message_type = o['type']
            if self.is_initialized is False and message_type != 'initialize':
                raise InvalidOperationException(
                    'socket should be initialized first')
            elif message_type == 'initialize':
                reply = self.init(o)
            elif message_type == 'get_subject':
                reply = self.get_subject(o)
            elif message_type == 'set_subject':
                reply = self.set_subject(o)
            elif message_type == 'get_subjects':
                reply = self.get_subjects(o)
            elif message_type == 'authorize':
                reply = self.authorize(o)
            else:
                raise InvalidOperationException('Unknown message type')
            self.send(message_type, reply, id)
        except InvalidMessageException as e:
            self.send('invalid_message', str(e), id)
        except InvalidOperationException as e:
            self.send('invalid_operation', str(e), id)
        except UnauthorizedOperationException as e:
            self.send('unauthorized_operation', str(e), id)
        except Exception as e:
            self.send('internal_error', traceback.format_exc(), id)
        else:
            self.notify(message_type, reply)

    def send(self, message_type='reply', message=None, id=None):
        m = dict(
            type=message_type,
            timestamp=int(time.time() * 1000),
            data=message
        )
        if id is not None:
            m['id'] = id
        self.write_message(json.dumps(m))

    def notify(self, message_type, message, is_global=False):
        for s in self.application.sockets.values():
            if s is not self and (is_global or s.is_experimenter):
                s.send(message_type, message)

    def check_data(self, message, keys=[]):
        if 'data' not in message or message['data'] is None:
            raise InvalidOperationException('Message should contain "data"')
        if len(keys) > 0:
            data = message['data']
            for key in keys:
                if key not in data or not data[key] or not data[key].strip():
                    raise InvalidOperationException(
                        'Message "data" should contain a "{0}"'.format(key)
                        )

    def check_experimenter(self):
        if not self.is_experimenter:
            raise UnauthorizedOperationException('Access denied')

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
        if 'data' in message and message['data'] is not None:
            key = self.parse_key(message['data'])
            if key is not None:
                socket = self.application.get_socket(key)
                if socket is not None:
                    socket.close()
                del self.application.sockets[self.key]
                self.key = key
                self.application.sockets[self.key] = self
                exp = self.application.get_experimenter(self.key)
                if exp is not None:
                    self.is_experimenter = True
        data['key'] = self.key
        data['session'] = dict(
            key=str(self.session.key),
            is_started=self.session.is_started,
            is_finished=self.session.is_finished
            )
        data['is_experimenter'] = self.is_experimenter
        self.is_initialized = True
        return data

    def get_subject(self, message):
        subject = None
        key = None
        if self.is_experimenter:
            self.check_data(message)
            key = message['data']
        else:
            key = self.key
            subject = self.application.get_subject(key)
            if subject is None:
                subject = zook.Subject(self.session, self.key)
                self.application.set_subject(subject)
        o = None
        if subject is not None:
            o = subject.to_dict()
        return o

    def get_subjects(self, message):
        self.check_experimenter()
        ss = []
        for s in self.application.subjects.values():
            ss.append(s.to_dict())
        return ss

    def set_subject(self, message):
        subject = None
        key = None
        if self.is_experimenter:
            self.check_data(message, ['key'])
            key = data['key']
        else:
            self.check_data(message)
            key = self.key
        data = message['data']
        subject = self.application.get_subject(key)
        if subject is None:
            subject = zook.Subject(self.session, key)
            self.application.set_subject(subject)
        if 'name' in data:
            name = data['name']
            if not name or not name.strip():
                del self.application.subjects[key]
                raise InvalidOperationException('Client name can not be empty')
            s = self.application.get_subject(name)
            if s is not None:
                del self.application.subjects[key]
                raise InvalidOperationException('Client name already in use')
            subject.name = name
        elif not subject.name:
            del self.application.subjects[key]
            raise InvalidOperationException('Client name can not be empty')
        if 'status' in data:
            subject.status = data['status']
        return subject.to_dict()

    def delete_subject(self, message):
        self.check_data(message)
        self.check_experimenter(message)
        key = message['data']
        socket = self.application.get_socket(key)
        subject = self.application.get_subject(key)
        if socket is not None:
            socket.close()
        if subject is not None:
            del self.session.subjects[key]
            return True
        else:
            return False

    def authorize(self, message):
        if self.is_experimenter:
            raise InvalidOperationException('You already are authorized')
        self.check_data(message, ['login', 'password'])
        data = message['data']
        login = data['login']
        password = data['password']
        if login == 'exp' and password == '1':
            self.is_experimenter = True
            e = zook.Experimenter(self.session, self.key)
            self.application.set_experimenter(e)
            return True
        else:
            raise UnauthorizedOperationException()
