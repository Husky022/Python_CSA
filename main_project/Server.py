import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import select
from Socket import Socket
import pickle
import time
from logs import Logger
from datetime import datetime
import dis
import inspect
import socket

engine = create_engine('sqlite:///data.db', echo=True)

pool_recycle = 7200

metadata = MetaData()

users_table = Table('users', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('nickname', String),
                    Column('password', String)
                    )

users_history_table = Table('history', metadata,
                            Column('id', Integer, primary_key=True),
                            Column('user_id', ForeignKey('users.id')),
                            Column('ip_address', String),
                            Column('last_time', DateTime)
                            )

users_contacts = Table('contacts', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('user_id', ForeignKey('users.id')),
                       Column('id_contact', ForeignKey('users.id'))
                       )

metadata.create_all(engine)


# Таблицы БД

class User:
    def __init__(self, nickname, password):
        self.nickname = nickname
        self.password = password


class History:
    def __init__(self, user_id, ip_address, last_time):
        self.user_id = user_id
        self.ip_address = ip_address
        self.last_time = last_time


class Contacts:
    def __init__(self, user_id, id_contact):
        self.user_id = user_id
        self.id_contact = id_contact


u = mapper(User, users_table)
h = mapper(History, users_history_table)
c = mapper(Contacts, users_contacts)


def find_forbidden_methods_call(func, method_names):
    for instr in dis.get_instructions(func):
        if instr.opname == 'LOAD_METHOD' and instr.argval in method_names:
            return instr.argval


class ServerVerify(type):
    forbidden_method_names = ('connect')

    def __new__(cls, name, bases, class_dict):
        for _, value in class_dict.items():
            if inspect.isfunction(value):
                method_name = find_forbidden_methods_call(value, cls.forbidden_method_names)
                if method_name:
                    raise ValueError(f'called forbidden method "{method_name}"')
            elif isinstance(value, socket.socket):
                raise ValueError('Socket object cannot be defined in class definition')
        return type.__new__(cls, name, bases, class_dict)


class PortValidator:

    def __init__(self, default=7777):
        self.default = default
        self._value = None

    def __get__(self, instance, owner):
        return self._value or self.default

    def __set__(self, instance, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError('Incorrect port (Must be integer and positive)')
        self._value = value


class Server(Socket, metaclass=ServerVerify):
    port = PortValidator()

    def __init__(self):
        super(Server, self).__init__()
        self.clients = {}
        # self.logger = Logger.Logger.log(__name__)

    def set_up(self, socket_port):
        self.bind(('', socket_port))
        self.listen(5)
        self.settimeout(0.2)
        print('Server is ready')
        while True:
            try:
                client, addr = self.accept()
            except OSError as e:
                pass
            else:
                print("Connected %s" % str(addr))
                self.clients[client] = ''
            finally:
                wait = 10
                r = []
                w = []
                try:
                    r, w, e = select.select(list(self.clients.keys()), list(self.clients.keys()), [], wait)
                except:
                    pass
                requests = self.listen_socket(r, self.clients)
                if requests:
                    self.write_responses(requests, w, self.clients)

    def listen_socket(self, r_clients, all_clients):
        requests = {}
        for sock in r_clients:
            try:
                data = pickle.loads(sock.recv(1024))
                requests[sock] = data
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                Session = sessionmaker()
                Session.configure(bind=engine)
                session = Session()
                session.add(History("example_user_id", str(sock.getpeername()), datetime.now()))  # user_id для примера
                session.commit()
                del all_clients[sock]
        return requests

    def write_responses(self, requests, w_clients, all_clients):
        response = {
            "response": '',
            "time": time.ctime(),
            "resp_msg": '',
            "alert": ''
        }
        for sock in w_clients:
            if sock in requests:
                try:
                    data = requests[sock]
                    print(data)
                    if data['action'] == 'authenticate':
                        sock.send(pickle.dumps(self.client_authenticate(data, sock, response)))
                    elif data['action'] == 'available_commands':
                        sock.send(pickle.dumps(self.client_available_commands(response)))
                    elif data['action'] == 'msg':
                        sock.send(pickle.dumps(self.send_data(data, sock, response)))
                    elif data['action'] == 'available_users':
                        sock.send(pickle.dumps(self.client_available_users(response)))
                except:
                    print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                    Session = sessionmaker()
                    Session.configure(bind=engine)
                    session = Session()
                    session.add(
                        History("example_user_id", str(sock.getpeername()), datetime.now()))  # user_id для примера
                    session.commit()
                    self.logger.info(f'Отключен пользователь {all_clients[sock]}')
                    del all_clients[sock]
                    sock.close()

    def send_data(self, msg, cur_user, resp):
        if cur_user not in self.clients:
            resp = {
                "response": '401',
                "time": time.ctime(),
                "resp_msg": 'Для авторизации нажмите /auth',
                "alert": 'Не авторизован'
            }
            # self.logger.error(f'Ошибка авторизации при отправке сообщения {cur_user}')
        else:
            for k, v in self.clients.items():
                if k == cur_user:
                    from_user = v
                    break
            if msg['message'].startswith('@'):
                to_user = msg['message'][1:].split().pop(0)
                if to_user in self.clients.values():
                    msg.update(dict(from_user=from_user, to=to_user))
                    Session = sessionmaker()
                    Session.configure(bind=engine)
                    session = Session()
                    session.add(Contacts("example_from_user_id", "example_to_user_id"))  # user_id для примера
                    session.commit()
                    for k, v in self.clients.items():
                        if v == to_user:
                            k.send(pickle.dumps(msg))
                    # self.logger.info(f'Отправлено сообщение от {from_user} к {to_user}')
                    resp = {
                        "response": '200',
                        "time": time.ctime(),
                        "resp_msg": f'Отправлено пользователю {to_user}',
                        "alert": ''
                    }
                else:
                    resp = {
                        "response": '404',
                        "time": time.ctime(),
                        "resp_msg": '',
                        "alert": f'Ошибка. Пользователя {to_user} нет в сети'
                    }
                    # self.logger.error(f'Ошибка отправки сообщения от {cur_user}. Пользователя {to_user} нет в сети')
            else:
                msg.update(dict(from_user=from_user, to='All'))
                for k in self.clients:
                    if k != cur_user:
                        k.send(pickle.dumps(msg))
                # self.logger.info(f'Отправлено сообщение от {from_user} в общий чат')
                resp = {
                    "response": '200',
                    "time": time.ctime(),
                    "resp_msg": 'Отправлено в общий чат',
                    "alert": ''
                }
        cur_user.send(pickle.dumps(resp))

    def client_authenticate(self, msg, user, resp):
        if not self.clients.get(user):
            self.clients[user] = msg['user']['account_name']
            print(self.clients)
            resp['response'], resp['alert'], = '200', 'Авторизация прошла успешно'
            Session = sessionmaker()
            Session.configure(bind=engine)
            session = Session()
            session.add(User(msg['user']['account_name'], "password_example"))
            session.commit()
            # self.logger.info(f'Пользователь {user} авторизован')
        else:
            resp['response'], resp['alert'], = '409', 'Данный пользователь уже авторизован'
            # self.logger.warning(f'Ошибка авторизации. Повторная авторизация пользователя {user}')
        return resp

    def client_available_commands(self, resp):
        resp['response'] = '200'
        resp['resp_msg'] = 'Доступные комманды:\n/quit - выход\n' \
                           '/users - список пользователей\nдля отправки сообщения конкретному' \
                           ' пользователю\nиспользуйте конструкцию ::::@USER_NAME YOUR_MESSAGE'
        return resp

    def client_available_users(self, resp):
        resp['response'] = '200'
        resp['resp_msg'] = f'Пользователи в сети: {list(self.clients.values())}'
        return resp


if __name__ == '__main__':
    print("Версия SQLAlchemy:", sqlalchemy.__version__)
    server = Server()
    # server.port = 0
    print(f'Server.port = {server.port}')
    server.set_up(server.port)
