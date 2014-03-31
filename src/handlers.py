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
        self.subject = None
        self.key = uuid.uuid4()
        self.application.sockets[self.key] = self
        self.is_initialized = False
        self.is_experimenter = False

    def on_close(self):
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
            self.is_initialized = True
            return self.send('initialize', data, message['id'])
        except:
            return self.send('internal_error', str(traceback.format_exc()))

    def get_subject(self, message):
        return self.send('get_subject', self.subject, message['id'])

    def set_subject(self, message):
        if 'name' not in message:
            return send.message(
                'invalid_message',
                'message should contain a "name"'
                )
        if self.subject is None:
            self.subject