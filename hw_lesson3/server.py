from socket import *
import pickle
import time

import threading


server = socket(AF_INET, SOCK_STREAM)
server.bind(('', 7777))
server.listen(3)

clients = {}

response = {
    "response": '',
    "time": time.ctime(),
    "resp_msg": '',
    "alert": ''
}

def client_quit(cur_user):
    for k, v in clients.items():
        if v == cur_user:
            del clients[k]
            break
    response['response'], response['resp_msg'], = '200', 'Пользователь вышел'
    return response


def send_message(msg, cur_user):
    if cur_user not in clients.values():
        return {
            "response": '401',
            "time": time.ctime(),
            "resp_msg": 'Для авторизации нажмите /auth',
            "alert": 'Не авторизован'
        }
    else:
        for k, v in clients.items():
            if v == cur_user:
                from_user = k
                break
        if msg['message'].startswith('@'):
            to_user = msg['message'][1:].split().pop(0)
            msg['message'] = ' '.join(msg['message'][1:].split()[1:])
            msg.update(dict(from_user=from_user, to=to_user))
            try:
                clients[to_user].send(pickle.dumps(msg))
            except KeyError:
                return {
                    "response": '404',
                    "time": time.ctime(),
                    "resp_msg": 'Не отправлено. Такого получателя не существует',
                    "alert": ''
                }
        else:
            msg.update(dict(from_user=from_user, to='All'))
            for k in clients:
                if clients[k] != cur_user:
                    clients[k].send(pickle.dumps(msg))
        return {
            "response": '200',
            "time": time.ctime(),
            "resp_msg": 'Отправлено',
            "alert": ''
        }


def client_available_users():
    return {
        "response": '200',
        "time": time.ctime(),
        "resp_msg": list(clients.keys()),
        "alert": ''
    }


def client_available_commands():
    return {
        "response": '200',
        "time": time.ctime(),
        "resp_msg": 'Доступные комманды:\n/quit - выход\n'
                           '/users - список пользователей\nдля отправки сообщения конкретному'
                           ' пользователю\nиспользуйте конструкцию ::::@USER_NAME YOUR_MESSAGE',
        "alert": ''
    }

def client_authenticate(msg, user):
    if not clients.get(msg['user']['account_name']):
        clients[msg['user']['account_name']] = user
        print(clients)
        response['response'], response['resp_msg'], = '200', 'Авторизация прошла успешно'
    else:
        response['response'], response['resp_msg'], = '409', 'Данный пользователь уже авторизован'
    return response

def listen_user(user):
    global response
    while True:
        response = {
            "response": '',
            "time": time.ctime(),
            "resp_msg": '',
            "alert": ''
        }
        data = pickle.loads(user.recv(2048))
        print(data)
        if data['action'] == 'authenticate':
            user.send(pickle.dumps(client_authenticate(data, user)))
        elif data['action'] == 'available_commands':
            user.send(pickle.dumps(client_available_commands()))
        elif data['action'] == 'msg':
            user.send(pickle.dumps(send_message(data, user)))
        elif data['action'] == 'available_users':
            user.send(pickle.dumps(client_available_users()))
        elif data['action'] == 'quit':
            user.send(pickle.dumps(client_quit(user)))
        print()


def start_server():
    while True:
        client, addr = server.accept()
        print("Connected %s" % str(addr))
        listen_accepted_user = threading.Thread(target=listen_user, args=(client,))
        listen_accepted_user.start()


if __name__ == '__main__':
    start_server()