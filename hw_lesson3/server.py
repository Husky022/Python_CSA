from socket import *
import pickle
import time

s = socket(AF_INET, SOCK_STREAM)
s.bind(('', 7777))
s.listen(3)

client_auth = {} # Эмуляция бд с полем для аутентификации пользователя
clients = {}


def client_presence():
    global response
    response = {
        "response": 200,
        "time": time.ctime()
    }
    client.send(pickle.dumps(response))


def client_authenticate():
    global response
    if not client_auth.get(msg['user']['account_name']):
        client_auth[msg['user']['account_name']] = True
        clients[msg['user']['account_name']] = client
        print(clients)
        response = {
            "response": 200,
            "time": time.ctime(),
            "alert": 'Авторизация прошла успешно'
        }
    else:
        # Здесь должна быть проверка пароля
        response = {
            "response": 409,
            "time": time.ctime(),
            "alert": "Данный пользователь уже авторизован"
        }
    client.send(pickle.dumps(response))


def client_quit():
    global response
    client_auth[msg['user']['account_name']] = False
    response = {
        "response": 200,
        "time": time.ctime(),
        "alert": 'Пользователь вышел'
    }
    client.send(pickle.dumps(response))


def user_to_user_message():
    client = clients[msg['to']]
    client.send(pickle.dumps(msg))


actions = {
    'presence': client_presence,
    'authenticate': client_authenticate,
    'quit': client_quit,
    'msg': user_to_user_message

}

while True:
    client, addr = s.accept()
    print("Получен запрос на соединение от %s" % str(addr))
    print(client)
    msg = pickle.loads(client.recv(1024))
    print(msg)
    if not actions.get(msg['action']):
        response = {
            "response": 400,
            "time": time.ctime(),
            "alert": "Неправильный запрос/JSON-объект"
        }
        client.send(pickle.dumps(response))
    else:
        actions.get(msg['action'])()

