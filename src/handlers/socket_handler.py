import tornado.websocket
import datetime, time
import json
import uuid

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