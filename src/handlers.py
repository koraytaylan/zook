import zook
import tornado.websocket
import uuid
import time
import ujson as json
import codecs
import os
import sys
import traceback
import re
import openpyxl
from collections import OrderedDict


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


class ExportHandler(tornado.web.RequestHandler):
    """docstring for ExportHandler"""
    def get(self):
        key = self.get_argument('key')
        self.render(key)
        file_name = 'session-' + key + '.xlsx'
        path = os.path.join(self.application.data_path, file_name)
        buf_size = 4096
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        with open(path, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()

    def render(self, key):
        wb = openpyxl.Workbook(encoding='utf-8')
        ws = wb.active
        path_json = os.path.join(self.application.data_path, 'session-' + key + '.json')
        path_xlsx = os.path.join(self.application.data_path, 'session-' + key + '.xlsx')
        data = None
        with open(path_json, 'r') as f:
            data = json.load(f)
        row = 0
        headers = (
            'Phase',
            'Period',
            'Group',
            'Subject',
            'UnitCost',
            'QuantityInitial',
            'QuantityReached',
            'Direction',
            'UpCovered',
            'DownCovered',
            'CoinFlip',
            'Outcome',
            'Role',
            'Provide',
            'Bid',
            'Ask',
            'PeriodStartingBalance',
            'PhaseStartingBalance',
            'Balance',
            'PeriodProfit',
            'PhaseProfit',
            'TotalProfit'
        )
        col = 0
        for h in headers:
            cell = ws.cell(row=row, column=col)
            cell.value = h
            cell.style.font.bold = True
            # ws.column_dimensions[openpyxl.cell.get_column_letter(col + 1)].width = 15
            col += 1
        row += 1
        col = 0
        phases = OrderedDict(sorted(data['phases'].items(), key=lambda t: int(t[0])))
        for i, ph in enumerate(phases.values()):
            periods = OrderedDict(sorted(ph['periods'].items(), key=lambda t: int(t[0])))
            for j, pe in enumerate(periods.values()):
                groups = OrderedDict(sorted(pe['groups'].items(), key=lambda t: int(t[0])))
                for k, g in enumerate(groups.values()):
                    subjects = OrderedDict(sorted(g['subjects'].items(), key=lambda t: t[1]['name']))
                    for s in subjects.values():
                        col = 0
                        cells = self.generate_row(ph, pe, g, s)
                        for c in cells:
                            ws.cell(row=row, column=col).value = c
                            col += 1
                        row += 1
        wb.save(path_xlsx)

    def set_cell_value(self, ws, row, column, value, centered=False):
        c = ws.cell(row=row, column=column)
        if centered:
            c.style.alignment.horizontal = 'center'
            c.style.alignment.vertical = 'center'
        c.value = value

    def generate_row(self, ph, pe, g, s):
        role = None
        provide = None
        bid = None
        ask = None
        period_profit = None
        period_balance = None
        phase_profit = None
        phase_balance = None
        if s['key'] in g['roles']:
            role = g['roles'][s['key']]
        if s['key'] in g['provides']:
            provide = g['provides'][s['key']]
        if s['key'] in g['bids']:
            bid = g['bids'][s['key']]
        if s['key'] in g['asks']:
            ask = g['asks'][s['key']]
        if s['key'] in pe['balances']:
            period_balance = pe['balances'][s['key']]
        if s['key'] in pe['profits']:
            period_profit = pe['profits'][s['key']]
        if s['key'] in ph['balances']:
            phase_balance = ph['balances'][s['key']]
        if s['key'] in ph['profits']:
            phase_profit = ph['profits'][s['key']]
        row = (
            ph['key'],
            pe['key'],
            g['key'],
            s['name'],
            pe['cost'],
            g['quantity_initial'],
            g['quantity_reached'],
            g['direction'],
            g['up_covered'],
            g['down_covered'],
            g['coin_flip'],
            g['outcome'],
            role,
            provide,
            bid,
            ask,
            period_balance,
            phase_balance,
            s['current_balance'],
            period_profit,
            phase_profit,
            s['total_profit']
        )
        return row

    def render_(self, key):
        wb = openpyxl.Workbook(encoding='utf-8')
        ws = wb.active
        path_json = os.path.join(self.application.data_path, 'session-' + key + '.json')
        path_xlsx = os.path.join(self.application.data_path, 'session-' + key + '.xlsx')
        data = None
        with open(path_json, 'r') as f:
            data = json.load(f)
        ws['A3'] = 'Name'
        ws['B3'] = 'Balance'
        ws['C3'] = 'Total Profit'
        ws['D3'] = 'Suspended'
        phases = OrderedDict(sorted(data['phases'].items(), key=lambda t: int(t[0])))
        row = 0
        col = 4
        for i, ph in enumerate(phases.values()):
            row = 0
            ws.cell(row=row, column=col).value = 'Phase ' + str(ph['key'])
            periods = OrderedDict(sorted(ph['periods'].items(), key=lambda t: int(t[0])))
            for j, pe in enumerate(periods.values()):
                row = 1
                ws.cell(row=row, column=col).value = 'Period ' + str(pe['key'])
                ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+4)
                row = 2
                ws.cell(row=row, column=col).value = 'Cost'
                ws.cell(row=row, column=col+1).value = 'Profit'
                ws.cell(row=row, column=col+2).value = 'Provide'
                ws.cell(row=row, column=col+3).value = 'Bid'
                ws.cell(row=row, column=col+4).value = 'Ask'
                col += 5
            #col += len(periods) + 4 + i
        for i, s in enumerate(data['subjects'].values()):
            ws.cell(row=i+3, column=0).value = s['name']
            ws.cell(row=i+3, column=1).value = s['current_balance']
            ws.cell(row=i+3, column=2).value = s['total_profit']
            ws.cell(row=i+3, column=3).value = s['is_suspended'] or s['is_robot']
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15
        for r in list(range(3)):
            for c in list(range(col)):
                ws.cell(row=r, column=c).style.font.bold = True
        wb.save(path_xlsx)


class InvalidOperationException(Exception):
    pass


class UnauthorizedOperationException(Exception):
    pass


class InvalidMessageException(Exception):
    pass


class SocketHandler(tornado.websocket.WebSocketHandler):
    """docstring for SocketHandler"""
    def open(self):
        self.is_open = True
        self.key = str(uuid.uuid4())
        self.application.sockets[self.key] = self
        self.session = self.find_session()
        self.is_initialized = False
        self.is_experimenter = False
        self.timer = None
        self.timer_started_at = None

    def on_close(self):
        self.is_open = False
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
            elif message_type == 'pause_session':
                reply = self.pause_session(o)
            elif message_type == 'resume_session':
                reply = self.resume_session(o)
            elif message_type == 'stop_session':
                reply = self.stop_session(o)
            elif message_type == 'continue_session':
                reply = self.continue_session(o)
            elif message_type == 'skip_phase':
                reply = self.skip_phase(o)
            elif message_type == 'reset':
                reply = self.reset(o)
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
        js = json.dumps(m)
        self.write_message(js)
        del m
        del js

    def notify(self, message_type, message, is_global=False):
        ignore_list = (
            'initialize',
            'authorize',
            'get_session'
            )
        if message_type not in ignore_list:
            for e in self.session.experimenters.values():
                socket = self.application.get_socket(e.key)
                if socket is not None and socket.is_open and e.key is not self.key:
                    ses = self.application.clone_session(self.session)
                    socket.send('get_session', ses)

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
                (s for s in self.application.sessions.values()),
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
                if socket is not None and socket.is_open:
                    socket.close()
                del self.application.sockets[self.key]
                self.key = key
                self.application.sockets[self.key] = self
                exp = self.application.get_experimenter(self.key)
                if exp is not None:
                    self.is_experimenter = True
                    self.session = exp.session
                else:
                    sub = self.application.get_subject(self.key)
                    if sub is not None:
                        self.session = sub.session
                        if zook.Subject.states[sub.state] == 'dropped':
                            sub.restore_state()
                    else:
                        self.session = self.find_session()

        data['key'] = self.key
        data['session'] = self.application.clone_session(self.session)
        data['is_experimenter'] = self.is_experimenter
        self.is_initialized = True
        return data

    def get_session(self, message):
        ses = self.application.clone_session(self.session)
        return ses

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
        return self.application.clone_subject(subject)

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
        if socket is not None and socket.is_open:
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
        subject = self.application.get_subject(key)
        if subject is not None:
            subject.is_suspended = True
            subject.set_state('robot')
            socket = self.application.get_socket(key)
            if socket is not None and socket.is_open:
                sub = self.application.clone_subject(subject)
                socket.send('get_subject', sub)
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
        ss = self.session.get_subjects_by_active()
        if len(ss) < 2:
            raise InvalidOperationException('There should be at least 2 active clients to start a session')
        self.application.start_session(self.session)
        ses = self.application.clone_session(self.session)
        return ses

    def pause_session(self, message):
        self.check_experimenter()
        if not self.session.is_started:
            raise InvalidOperationException('Session is not started')
        self.application.pause_session(self.session)
        ses = self.application.clone_session(self.session)
        return ses

    def resume_session(self, message):
        self.check_experimenter()
        if not self.session.is_started:
            raise InvalidOperationException('Session is not paused')
        self.application.resume_session(self.session)
        ses = self.application.clone_session(self.session)
        return ses

    def stop_session(self, message):
        self.check_experimenter()
        self.application.stop_session(self.session)
        ses = self.application.clone_session(self.session)
        return ses

    def continue_session(self, message):
        self.check_data(message)
        self.set_subject(message)
        subject = self.application.get_subject(self.key)
        if self.session.is_started:
            self.application.clear_timer(self.key)
            self.process_input()
            self.application.proceed(self.session)
        s = self.application.clone_subject(subject)
        return s

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
        ses = self.application.clone_session(self.session)
        return ses

    def reset(self, message):
        self.check_experimenter()
        ss = self.session.subjects.items()
        es = self.session.experimenters.items()
        self.application.sessions.pop(self.session.key, None)
        session = zook.Session()
        self.application.sessions[session.key] = session
        self.session = session
        session.experimenters[self.key] = self.application.experimenters[self.key]
        for key, s in ss:
            self.application.subjects.pop(key, None)
            socket = self.application.get_socket(key)
            if socket is not None and socket.is_open:
                socket.close()
        ses = self.application.clone_session(self.session)
        for key, e in es:
            if key is self.key:
                continue
            e.session = session
            session.experimenters[key] = e
            socket = self.application.get_socket(key)
            if socket is not None and socket.is_open:
                socket.send('get_session', ses)
        return ses