from Socket import Socket
from threading import Thread
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


    def set_up(self):
        self.connect(('localhost', 7777))
        listen_thread_1 = Thread(target=self.listen_socket)
        listen_thread_1.start()
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

        while True:
            request = {
                "action": '',
                "time": time.ctime()
            }
            print()
            time.sleep(0.2)
            client_message = input('\nSend message/command or Press /help:::')
            self.send_data_to_server(client_message, request)


    def create_new_user(self, current_user_name):
        print('новый юзер')
        password_1 = input('Придумайте пароль: ')
        # while True:
        #     print('password_1')
        #     password_1 = input('Придумайте пароль:')
        #     print('password_2')
        #     password_2 = input('Повторите пароль:')
        #     print('after password_2')
        #     if password_1 != password_2:
        #         print('Пароли не совпадают! Повторите попытку!')
        #     else:
        #         break
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
        print('старый юзер')
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
            data = pickle.loads(self.recv(2048))
            if not data:
                continue
            elif 'response' in data:
                if data['response'] == '200':
                    print(data['resp_msg'])
                if data['response'] == '201':
                    print(data)
                    self.send(pickle.dumps(self.create_new_user(data['username'])))
                if data['response'] in ['202', '444']:
                    print(data['alert'])
                    self.user_authenticate(data['username'])
                if data['response'] in ['401', '404', '409']:
                    print(data['alert'])
            else:
                print(f'Cообщение от {data["from_user"]}: {data["message"]}')



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


if __name__ == '__main__':
    client = Client()
    client.set_up()
