from socket import *
import time
import pickle
from threading import Thread, Lock
import sys


sys.path.append("../hw_lesson5_log/")
import client_log_config

locker = Lock()


def get_connect():
    global client, logger
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(('localhost', 7777))
    logger = client_log_config.get_logger(__name__)
    logger.info(f'Клиент {client} запущен')
    listen_thread = Thread(target=listen_server)
    listen_thread.start()


def request_available_users():
    request['action'] = 'available_users'
    return request

def request_available_commands():
    request['action'] = 'available_commands'
    return request

def listen_server():
    global data
    while True:
        try:
            data = pickle.loads(client.recv(2048))
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


def send_request(request_message):
    if request_message.lower() == '/help':
        client.send(pickle.dumps(request_available_commands()))
    elif request_message.lower() == '/quit':
        client.close()
        sys.exit()
    elif request_message.lower() == '/users':
        client.send(pickle.dumps(request_available_users()))
    else:
        request['action'], request['message'] = 'msg', request_message
        logger.info(f'Клиент {client} отправил сообщение {request_message}')
        client.send(pickle.dumps(request))

def start_client():
    global request
    get_connect()
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
    client.send(pickle.dumps(request))
    while True:
        request = {
            "action": '',
            "time": time.ctime()
        }
        print()
        time.sleep(0.2)
        client_message = input('\nSend message/command or Press /help:::')
        send_request(client_message)


# if __name__ == '__main__':
start_client()