from socket import *
import time
import pickle
import threading
import sys


sys.path.append("../hw_lesson5_log/")
import client_log_config

client = socket(AF_INET, SOCK_STREAM)
client.connect(('localhost', 7777))


def quit():
    request['action'] = 'quit'
    return request


def request_available_users():
    request['action'] = 'available_users'
    return request

def request_available_commands():
    request['action'] = 'available_commands'
    return request

def listen_server():
    while True:
        data = pickle.loads(client.recv(2048))
        print(data, '\n')


def start_client():
    global request, logger
    logger = client_log_config.get_logger(__name__)
    logger.info(f'Клиент {client} запущен')
    listen_thread = threading.Thread(target=listen_server)
    listen_thread.start()
    username = input('Введите имя:')
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
        client_message = input('Send message/command or Press /help:::')
        if client_message.lower() == '/help':
            client.send(pickle.dumps(request_available_commands()))
        elif client_message.lower() == '/quit':
            client.send(pickle.dumps(quit()))
        elif client_message.lower() == '/users':
            client.send(pickle.dumps(request_available_users()))
        else:
            request['action'], request['message']  = 'msg', client_message
            logger.info(f'Клиент {client} отправил сообщение {client_message}')
            client.send(pickle.dumps(request))


if __name__ == '__main__':
    start_client()