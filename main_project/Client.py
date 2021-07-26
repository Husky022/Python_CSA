from Socket import Socket
from threading import Thread
import pickle
import sys
import time
import dis
import inspect
import socket


def find_forbidden_methods_call(func, method_names):
    for instr in dis.get_instructions(func):
        if instr.opname == 'LOAD_METHOD' and instr.argval in method_names:
            return instr.argval


class ClientVerify(type):
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


class Client(Socket, metaclass=ClientVerify):
    def __init__(self):
        super(Client, self).__init__()

    def set_up(self):
        self.connect(('localhost', 7777))
        listen_thread = Thread(target=self.listen_socket)
        listen_thread.start()
        username = input('Введите имя:')
        while not username:
            username = input('Имя не может быть пустым! Введите имя:')
        request = {
            "action": "authenticate",
            "time": time.ctime(),
            "user": {
                "account_name": username,
                "password": ''
            }
        }
        self.send(pickle.dumps(request))
        while True:
            request = {
                "action": '',
                "time": time.ctime()
            }
            print()
            time.sleep(0.2)
            client_message = input('\nSend message/command or Press /help:::')
            self.send_data(client_message, request)

    def listen_socket(self):
        while True:
            try:
                data = pickle.loads(self.recv(2048))
            except ConnectionAbortedError:
                print('Отключение от сервера')
                sys.exit()
            try:
                print(data['alert'])
            except:
                pass
            try:
                print(data['resp_msg'])
            except:
                pass
            try:
                print(f'Cообщение от {data["from_user"]}: {data["message"]}')
            except:
                pass

    def send_data(self, request_message, request):
        if request_message.lower() == '/help':
            self.send(pickle.dumps(self.request_available_commands(request)))
        elif request_message.lower() == '/quit':
            self.close()
            sys.exit()
        elif request_message.lower() == '/users':
            self.send(pickle.dumps(self.request_available_users(request)))
        else:
            request['action'], request['message'] = 'msg', request_message
            # logger.info(f'Клиент {client} отправил сообщение {request_message}')
            self.send(pickle.dumps(request))

    def request_available_users(self, request):
        request['action'] = 'available_users'
        return request

    def request_available_commands(self, request):
        request['action'] = 'available_commands'
        return request



if __name__ == '__main__':
    client = Client()
    client.set_up()