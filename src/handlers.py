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
import threading
import re


def to_dict(obj, classkey=None, ignores=None):
    if ignores is not None and obj in ignores:
        return None
    elif isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = to_dict(v, classkey, ignores)
        return data
    elif isinstance(obj, list):
        data = []
        for v in obj:
            data.append(to_dict(v, classkey, ignores))
        return data
    elif hasattr(obj, "_ast"):
        return to_dict(obj._ast())
    elif hasattr(obj, "__dict__"):
        igs = [obj]
        if ignores is not None:
            igs.extend(ignores)
        data = dict([(key, to_dict(value, classkey, igs))
                    for key, value in obj.__dict__.items()
                    if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    # elif hasattr(obj, "__iter__"):
    #    return [to_dict(v, classkey, ignores) for v in obj]
    else:
        return obj


if __name__ == "__main__":
    s = zook.Session()
    p = zook.Phase(s, 0)
    pp = zook.Period(p, 0)
    g = zook.Group(pp, 0)
    ss = zook.Subject(s)
    print(json.dumps(to_dict(ss)))


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
        self.timer = None
        self.timer_started_at = None

    def on_close(self):
        if hasattr(self, 'key'):
            del self.application.sockets[self.key]
            s = self.application.get_subject(self.key)
            if s is not None:
                s.set_state('dropped')
                self.notify('set_subject', s)

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
            elif message_type == 'get_session':
                reply = self.get_session(o)
            elif message_type == 'get_group':
                reply = self.get_group(o)
            elif message_type == 'get_subject':
                reply = self.get_subject(o)
            elif message_type == 'set_subject':
                reply = self.set_subject(o)
            elif message_type == 'get_subjects':
                reply = self.get_subjects(o)
            elif message_type == 'authorize':
                reply = self.authorize(o)
            elif message_type == 'suspend_subject':
                reply = self.suspend_subject(o)
            elif message_type == 'start_session':
                reply = self.start_session(o)
            elif message_type == 'stop_session':
                reply = self.stop_session(o)
            elif message_type == 'continue_session':
                reply = self.continue_session(o)
            elif message_type == 'skip_phase':
                reply = self.skip_phase(o)
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
        m = to_dict(m)
        self.write_message(json.dumps(m))

    def notify(self, message_type, message, is_global=False):
        for s in self.application.sockets.values():
            if s is not self and (is_global or s.is_experimenter):
                s.send(message_type, message)

    @staticmethod
    def check_data(message, keys=[]):
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
                else:
                    sub = self.application.get_subject(self.key)
                    if sub is not None:
                        self.session = sub.session
                        if sub.is_suspended:
                            raise InvalidOperationException(
                                'Your client has been suspended')
                        elif zook.Subject.states[sub.state] == 'dropped':
                            sub.restore_state()

        data['key'] = self.key
        data['session'] = self.session.__dict__
        data['is_experimenter'] = self.is_experimenter
        self.is_initialized = True
        return data

    def get_session(self, message):
        return self.session

    def get_group(self, message):
        group = None
        key = None
        if self.session.is_started:
            if self.is_experimenter:
                self.check_data(message)
                key = message['data']
                period = self.application.get_current_period(self.session)
                group = period.groups[key]
            else:
                subject = self.application.get_subject(self.key)
                if 'data' in message and message['data'] != subject.group_key:
                    raise InvalidOperationException()
                group = subject.group
        return group

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
        return subject

    def get_subjects(self, message):
        self.check_experimenter()
        ss = []
        for s in self.application.subjects.values():
            ss.append(s)
        return ss

    def set_subject(self, message):
        subject = None
        key = None
        if self.is_experimenter:
            self.check_data(message, ['key'])
            data = message['data']
            key = data['key']
        else:
            self.check_data(message)
            key = self.key
        data = message['data']
        subject = self.application.get_subject(key)
        if subject is None:
            subject = zook.Subject(self.session, key)
            self.application.set_subject(subject)
        if 'name' in data \
                and (self.is_experimenter or not subject.is_initialized):
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
            raise InvalidOperationException('Client name can not be empty')
        if 'my_provide' in data:
            subject.my_provide = data['my_provide']
        if 'my_bid' in data:
            subject.my_bid = data['my_bid']
        if 'my_ask' in data:
            subject.my_ask = data['my_ask']
        subject.decide_state()
        return subject

    def delete_subject(self, message):
        self.check_data(message)
        self.check_experimenter()
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

    def suspend_subject(self, message):
        self.check_data(message)
        self.check_experimenter()
        key = message['data']
        socket = self.application.get_socket(key)
        subject = self.application.get_subject(key)
        if socket is not None:
            socket.close()
        if subject is not None:
            subject.is_suspended = True
            subject.set_state('passive')
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

    def start_session(self, message):
        self.check_experimenter()
        self.application.start_session(self.session)
        return self.session

    def stop_session(self, message):
        self.check_experimenter()
        self.application.stop_session(self.session)
        return self.session

    def continue_session(self, message):
        self.check_data(message)
        self.clear_timer()
        self.set_subject(message)
        subject = self.application.get_subject(self.key)
        if self.session.is_started:
            self.process_input()
            self.application.proceed(self.session)
        return subject

    def set_timer(self, seconds, func, args=None):
        self.timer_started_at = int(time.time() * 1000)
        self.timer = threading.Timer(seconds, func, args)
        self.timer.start()

    def clear_timer(self):
        if self.timer is not None:
            self.timer.cancel()
            self.timer_started_at = None

    def input_timeout(self):
        subject = self.application.get_subject(self.key)
        subject.set_state('waiting')
        self.application.proceed(self.session)
        self.send('continue_session', subject)

    def process_input(self):
        subject = self.application.get_subject(self.key)
        group = subject.group
        if group.stage == 0:
            if subject.my_provide is None:
                raise InvalidOperationException(
                    'A default value will be used for you'
                    + ' unless you enter a valid number.')
            elif re.match('^\d+(\.\d+){0,1}$', subject.my_provide) is None \
                    or float(subject.my_provide) < 0 \
                    or float(subject.my_provide) > 4 \
                    or (
                        float(subject.my_provide) - float(subject.my_provide) > 0
                        and float(subject.my_provide) - float(subject.my_provide) != 0.5
                        ):
                raise InvalidOperationException(
                    'The quantity must be at least 0,'
                    + ' at most 4, and a multiple of 1/2.'
                    )

    def skip_phase(self, message):
        self.check_experimenter()
        if self.session.is_started:
            self.session.phase.is_skipped = True
        return True