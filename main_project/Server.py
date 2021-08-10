import sqlalchemy
from sqlalchemy import  create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import select
from Socket import Socket
import pickle
import time
from logs import Logger
from datetime import datetime


engine = create_engine('sqlite:///data.db', echo=True)

pool_recycle = 7200

Base = declarative_base()

# Таблицы БД

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    password = Column(String)

    def __init__(self, nickname, password):
        self.nickname = nickname
        self.password = password


class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    ip_address = Column(String)
    username = Column(String)
    last_time = Column(DateTime)


    def __init__(self, ip_address, username, last_time):
        self.ip_address = ip_address
        self.username = username
        self.last_time = last_time


class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    username_from = Column(String, ForeignKey('users.nickname'))
    username_to = Column(String, ForeignKey('users.nickname'))

    def __init__(self, username_from, username_to):
        self.username_from = username_from
        self.username_to = username_to

Base.metadata.create_all(engine)



# class VerifyMeta(type):
#     def __init__(self, clsname, bases, clsdict):
#         print(dir(self))
#         # key = "send_data"
#         # if key not in clsdict.keys():
#         #     raise TypeError(f'Отсуствует функция {key}')
#
#         type.__init__(self, clsname, bases, clsdict)
#
#
# class ServerVerifier(metaclass=VerifyMeta):
#     pass


class Server(Socket):
    def __init__(self):
        super(Server, self).__init__()
        print('Server is ready')
        self.clients_online = {}
        # self.logger = Logger.Logger.log(__name__)


    def set_up(self):
        self.bind(('', 7777))
        self.listen(5)
        self.settimeout(0.2)
        while True:
            try:
                client, addr = self.accept()
            except OSError as e:
                pass
            else:
                print("Connected %s" % str(addr))
                self.clients_online[client] = ''
            finally:
                wait = 10
                r = []
                w = []
                try:
                    r, w, e = select.select(list(self.clients_online.keys()), list(self.clients_online.keys()), [], wait)
                except:
                    pass
                requests = self.listen_socket(r, self.clients_online)
                if requests:
                    self.write_responses(requests, w, self.clients_online)


    def listen_socket(self, r_clients, all_clients):
        requests = {}
        for sock in r_clients:
            try:
                data = pickle.loads(sock.recv(1024))
                requests[sock] = data
            except:
                outgoing_user = self.clients_online[sock]
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                Session = sessionmaker()
                Session.configure(bind=engine)
                session = Session()
                session.add(History(outgoing_user, str(sock.getpeername()), datetime.now())) # user_id для примера
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
                    if data['action'] == 'authenticate_new':
                        sock.send(pickle.dumps(self.client_authenticate_new(data, sock, response)))
                    if data['action'] == 'authenticate_old':
                        sock.send(pickle.dumps(self.client_authenticate_old(data, sock, response)))
                    elif data['action'] == 'available_commands':
                        sock.send(pickle.dumps(self.client_available_commands(response)))
                    elif data['action'] == 'msg':
                        sock.send(pickle.dumps(self.send_data(data, sock)))
                    elif data['action'] == 'available_users':
                        sock.send(pickle.dumps(self.client_available_users(response)))
                    elif data['action'] == 'get_contacts':
                        sock.send(pickle.dumps(self.client_contacts(response, sock)))
                    elif data['action'] == 'identification':
                        sock.send(pickle.dumps(self.client_identification(data, response)))
                    elif data['action'].startswith('/del'):
                        sock.send(pickle.dumps(self.client_delete_contact(data, response, sock)))
                except:
                    outgoing_user = self.clients_online[sock]
                    print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                    Session = sessionmaker()
                    Session.configure(bind=engine)
                    session = Session()
                    session.add(History(outgoing_user, str(sock.getpeername()), datetime.now()))  # user_id для примера
                    session.commit()
                    # self.logger.info(f'Отключен пользователь {all_clients[sock]}')
                    del all_clients[sock]
                    sock.close()


    def send_data(self, msg, cur_user):
        if cur_user not in self.clients_online:
            resp = {
                "response": '401',
                "time": time.ctime(),
                "resp_msg": 'Для авторизации нажмите /auth',
                "alert": 'Не авторизован'
            }
            # self.logger.error(f'Ошибка авторизации при отправке сообщения {cur_user}')
        else:
            for k, v in self.clients_online.items():
                if k == cur_user:
                    from_user = v
                    break
            if msg['message'].startswith('@'):
                to_user = msg['message'][1:].split().pop(0)
                if to_user in self.clients_online.values():
                    msg.update(dict(from_user=from_user, to=to_user))
                    Session = sessionmaker()
                    Session.configure(bind=engine)
                    session = Session()
                    contacts = session.query(Contacts).filter_by(username_from=msg['from_user']).all()
                    contacts_list = [x.username_to for x in contacts]
                    if to_user not in contacts_list:
                        Session = sessionmaker()
                        Session.configure(bind=engine)
                        session = Session()
                        session.add(Contacts(from_user, to_user))
                        session.commit()
                    for k, v in self.clients_online.items():
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
                for k in self.clients_online:
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


    def client_identification(self, msg, resp):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        users = session.query(User).all()
        all_users = [x.nickname for x in users]
        if msg['user']['account_name'] in all_users:
            resp['response'] = '202'
            resp['username'] = msg["user"]["account_name"]
            resp['resp_msg'] = f'С возвращением, {msg["user"]["account_name"]}!\n'
            return resp
        else:
            resp['response'] = '201'
            resp['username'] = msg["user"]["account_name"]
            resp['resp_msg'] = f'Добро пожаловать, {msg["user"]["account_name"]}!\n'
            return resp


    def client_authenticate_new(self, msg, user, resp):
        if msg['user']['account_name'] not in self.clients_online.values():
            self.clients_online[user] = msg['user']['account_name']
            resp['response'], resp['resp_msg'], = '200', 'Авторизация прошла успешно'
            Session = sessionmaker(bind=engine)
            session = Session()
            session.add(User(msg['user']['account_name'], msg['user']['password']))
            session.commit()
            # self.logger.info(f'Пользователь {user} авторизован')
        else:
            resp['response'], resp['alert'], = '409', 'Данный пользователь уже авторизован'
            # self.logger.warning(f'Ошибка авторизации. Повторная авторизация пользователя {user}')
        return resp


    def client_authenticate_old(self, msg, user, resp):
        if msg['user']['account_name'] not in self.clients_online.values():
            self.clients_online[user] = msg['user']['account_name']
            Session = sessionmaker(bind=engine)
            session = Session()
            password = (session.query(User).filter_by(nickname=msg['user']['account_name']).first()).password
            if password == msg['user']['password']:
                resp['response'], resp['resp_msg'], resp['username'] = '200', 'Авторизация прошла успешно', msg['user']['account_name']
            else:
                resp['response'], resp['alert'], resp['username'] = '444', 'Неверный пароль! Повторите попытку!', msg['user']['account_name']
            # self.logger.info(f'Пользователь {user} авторизован')
        else:
            resp['response'], resp['alert'], resp['username'] = '409', 'Данный пользователь уже авторизован', msg['user']['account_name']
            # self.logger.warning(f'Ошибка авторизации. Повторная авторизация пользователя {user}')
        return resp


    def client_available_commands(self, resp):
        resp['response'] = '200'
        resp['resp_msg'] = 'Доступные комманды:\n/quit - выход\n' \
                               '/users - список пользователей\n' \
                               '/contacts - список Ваших контактов\nдля отправки сообщения конкретному' \
                               ' пользователю используйте конструкцию ::::@USER_NAME YOUR_MESSAGE\n' \
                               'для удаления пользователя из списка контактов используйте конструкцию /del USER_NAME\n'

        return resp


    def client_available_users(self, resp):
        resp['response'] = '200'
        resp['resp_msg'] = f'Пользователи в сети: {list(self.clients_online.values())}'
        return resp


    def client_contacts(self, resp, cur_user):
        print(self.clients_online)
        request_from_user = self.clients_online[cur_user]
        print(request_from_user)
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        users = session.query(Contacts).filter_by(username_from=request_from_user).all()
        contacts = [x.username_to for x in users]
        resp['response'] = '200'
        resp['resp_msg'] = f'Ваши контакты: {contacts}'
        return resp


    def client_delete_contact(self, msg, resp, cur_user):
        request_from_user = self.clients_online[cur_user]
        deleting_contact = msg['action'][5:].split().pop(0)
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        deleting_record = session.query(Contacts).filter_by(username_from=request_from_user, username_to=deleting_contact).first()
        session.delete(deleting_record)
        session.commit()
        resp['response'] = '200'
        resp['resp_msg'] = f'Пользователь {deleting_contact} удален из контактов'
        return resp


if __name__ == '__main__':
    print("Версия SQLAlchemy:", sqlalchemy.__version__)
    server = Server()
    server.set_up()