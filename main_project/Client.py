from Socket import Socket
from threading import Thread, Lock, Event
import pickle
import sys
import time


class VerifyMeta(type):
    def __init__(self, clsname, bases, clsdict):
        print(dir(self))
        # key = "send_data"
        # if key not in clsdict.keys():
        #     raise TypeError(f'Отсуствует функция {key}')

        type.__init__(self, clsname, bases, clsdict)


class Client(Socket):
    def __init__(self):
        super(Client, self).__init__()
        self.event = Event()

    def set_up(self):
        self.connect(('localhost', 7777))
        listen_thread_1 = Thread(target=self.listen_socket)
        listen_thread_2 = Thread(target=self.send_message_or_command)
        username = input('Введите имя:')
        while not username:
            username = input('Имя не может быть пустым! Введите имя:')
        request = {
            "action": "identification",
            "time": time.ctime(),
            "user": {
                "account_name": username,
                "password": ''
            }
        }
        self.send(pickle.dumps(request))
        listen_thread_1.start()
        listen_thread_2.start()
        listen_thread_1.join()
        listen_thread_2.join()


    def send_message_or_command(self):
        while True:
            self.event.wait()
            request = {
                "action": '',
                "time": time.ctime()
            }
            client_message = input('\nSend message/command or Press /help:::')
            self.send_data_to_server(client_message, request)


    def create_new_user(self, current_user_name):
        self.event.clear()
        while True:
            password_1 = input('Придумайте пароль:')
            password_2 = input('Повторите пароль:')
            if password_1 != password_2:
                print('Пароли не совпадают! Повторите попытку!')
            else:
                print('Пароль принят!')
                break
        request = {
            'action': 'authenticate_new',
            "time": time.ctime(),
            "user": {
                "account_name": current_user_name,
                "password": password_1
            }
        }
        return request


    def user_authenticate(self, current_user_name):
        password = input('Введите пароль: ')
        request = {
            'action': 'authenticate_old',
            "time": time.ctime(),
            "user": {
                "account_name": current_user_name,
                "password": password
            }
        }
        return request


    def listen_socket(self):
        while True:
            self.event.clear()
            data = pickle.loads(self.recv(2048))
            if not data:
                continue
            elif 'response' in data:
                if data['response'] == '200':
                    print(data['resp_msg'])
                    self.event.set()
                if data['response'] == '201':
                    print(data['resp_msg'])
                    self.send(pickle.dumps(self.create_new_user(data['username'])))
                if data['response'] in ['202', '444']:
                    print(data['alert'])
                    self.send(pickle.dumps(self.user_authenticate(data['username'])))
                if data['response'] in ['401', '409']:
                    print(data['alert'])
                if data['response'] in ['404']:
                    print(data['alert'])
                    self.event.set()
            else:
                print(f'Cообщение от {data["from_user"]}: {data["message"]}')
                self.event.set()


    def send_data_to_server(self, request_message, request):
        if request_message.lower() == '/help':
            self.send(pickle.dumps(self.request_available_commands(request)))
        elif request_message.lower() == '/quit':
            self.close()
            sys.exit()
        elif request_message.lower() == '/users':
            self.send(pickle.dumps(self.request_available_users(request)))
        elif request_message.lower() == '/contacts':
            self.send(pickle.dumps(self.request_user_contacts(request)))
        elif request_message.lower().startswith('/del'):
            self.send(pickle.dumps(self.delete_contact(request, request_message)))
        else:
            request['action'], request['message'] = 'msg', request_message
            # logger.info(f'Клиент {client} отправил сообщение {request_message}')
            self.send(pickle.dumps(request))

    def request_available_users(self, request):
        request['action'] = 'available_users'
        return request

    def request_user_contacts(self, request):
        request['action'] = 'get_contacts'
        return request

    def request_available_commands(self, request):
        request['action'] = 'available_commands'
        return request

    def delete_contact(self, request, request_message):
        request['action'] = request_message
        return request

if __name__ == '__main__':
    client = Client()
    client.set_up()
