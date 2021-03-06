from socket import *
import pickle
import time
import sys
import threading
from functools import wraps
import inspect




sys.path.append("../hw_lesson5_log/")
import server_log_config

DEBUG = True

# def mockable(func):
#     @wraps(func)
#     def wrapper(*args,**kwargs):
#         func_name = func.__name__ + '_mock' if DEBUG else func.__name__
#         # f = getattr(sys.modules['__main__'], func_name)
#         # print(*inspect.getmembers(sys.modules['__main__'], inspect.isfunction), sep='\n')
#         # print(f)
#         # print(globals()[func_name])
#         return func
#     return wrapper()

response = {
    "response": '',
    "time": time.ctime(),
    "resp_msg": '',
    "alert": ''
}

@server_log_config.log
def client_quit(cur_user):
    for k, v in clients.items():
        if v == cur_user:
            logger.info(f'{clients[k]} вышел')
            del clients[k]
            break
    response['response'], response['resp_msg'], = '200', 'Пользователь вышел'
    return response


@server_log_config.log
# @mockable
def send_message(msg, cur_user):
    if cur_user not in clients.values():
        return {
            "response": '401',
            "time": time.ctime(),
            "resp_msg": 'Для авторизации нажмите /auth',
            "alert": 'Не авторизован'
        }
        logger.error(f'Ошибка авторизации при отправке сообщения {cur_user}')
        cur_user.send(pickle.dumps(response))
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
                logger.info(f'Отправлено сообщение от {from_user} к {to_user}')
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

            logger.info(f'Отправлено сообщение от {from_user} в общий чат')
        return {
            "response": '200',
            "time": time.ctime(),
            "resp_msg": 'Отправлено',
            "alert": ''
        }


@server_log_config.log
def send_message_mock(msg, cur_user):
    print(f'Тестовое сообщение {msg["message"]} от пользователя {cur_user}')

@server_log_config.log
def client_available_users():
    return {
        "response": '200',
        "time": time.ctime(),
        "resp_msg": list(clients.keys()),
        "alert": ''
    }

@server_log_config.log
def client_available_commands():
    response['response'] = '200'
    response['resp_msg'] = 'Доступные комманды:\n/quit - выход\n' \
                           '/users - список пользователей\nдля отправки сообщения конкретному' \
                           ' пользователю\nиспользуйте конструкцию ::::@USER_NAME YOUR_MESSAGE'
    return response

@server_log_config.log
def client_authenticate(msg, user):
    if not clients.get(msg['user']['account_name']):
        clients[msg['user']['account_name']] = user
        print(clients)
        response['response'], response['alert'], = '200', 'Авторизация прошла успешно'
        logger.info(f'Пользователь {user} авторизован')
    else:
        response['response'], response['alert'], = '409', 'Данный пользователь уже авторизован'
        logger.warning(f'Ошибка авторизации. Повторная авторизация пользователя {user}')
    return response

  
@server_log_config.log
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


@server_log_config.log
def start_server():
    global logger, clients
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('', 7777))
    server.listen(3)
    clients = {}
    logger = server_log_config.get_logger(__name__)
    logger.info('Сервер запущен')
    while True:
        client, addr = server.accept()
        logger.info(f'Подключен клиент {client} {addr}')
        print("Connected %s" % str(addr))
        listen_accepted_user = threading.Thread(target=listen_user, args=(client,))
        listen_accepted_user.start()


if __name__ == '__main__':
    start_server()