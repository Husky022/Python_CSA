import select
from socket import socket, AF_INET, SOCK_STREAM
import sys
import pickle
import time

sys.path.append("../hw_lesson5_log/")
import server_log_config


def read_requests(r_clients, all_clients):
   requests = {}

   for sock in r_clients:
       try:
           data = pickle.loads(sock.recv(1024))
           requests[sock] = data
       except:
           print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
           del all_clients[sock]
   return requests


def write_responses(requests, w_clients, all_clients):
   global response
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
                   sock.send(pickle.dumps(client_authenticate(data, sock)))
               elif data['action'] == 'available_commands':
                   sock.send(pickle.dumps(client_available_commands()))
               elif data['action'] == 'msg':
                   sock.send(pickle.dumps(send_message(data, sock)))
               elif data['action'] == 'available_users':
                   sock.send(pickle.dumps(client_available_users()))
               elif data['action'] == 'quit':
                   sock.send(pickle.dumps(client_quit(sock)))
               print()
           except:  # Сокет недоступен, клиент отключился
               print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
               del all_clients[sock]
               sock.close()

@server_log_config.log
def start_server():
   global clients, logger
   clients = {}
   logger = server_log_config.get_logger(__name__)
   server = socket(AF_INET, SOCK_STREAM)
   server.bind(('', 7777))
   server.listen(5)
   server.settimeout(0.2)
   while True:
       try:
           client, addr = server.accept()
       except OSError as e:
           pass
       else:
           print("Connected %s" % str(addr))
           clients[client] = ''
       finally:
           wait = 10
           r = []
           w = []
           try:
               r, w, e = select.select(list(clients.keys()), list(clients.keys()), [], wait)
           except:
               pass
           requests = read_requests(r, clients)
           if requests:
               write_responses(requests, w, clients)

@server_log_config.log
def client_quit(cur_user):
    del clients[cur_user]
    response['response'], response['resp_msg'], = '200', 'Пользователь вышел'
    return response


@server_log_config.log
# @mockable
def send_message(msg, cur_user):
    if cur_user not in clients:
        response = {
            "response": '401',
            "time": time.ctime(),
            "resp_msg": 'Для авторизации нажмите /auth',
            "alert": 'Не авторизован'
        }
        logger.error(f'Ошибка авторизации при отправке сообщения {cur_user}')
        cur_user.send(pickle.dumps(response))
    else:
        for k, v in clients.items():
            if k == cur_user:
                from_user = v
                break
        if msg['message'].startswith('@'):
            to_user = msg['message'][1:].split().pop(0)
            msg.update(dict(from_user=from_user, to=to_user))
            for k, v in clients.items():
                if v == to_user:
                    k.send(pickle.dumps(msg))
            logger.info(f'Отправлено сообщение от {from_user} к {to_user}')
        else:
            msg.update(dict(from_user=from_user, to='All'))
            for k in clients:
                if k != cur_user:
                    k.send(pickle.dumps(msg))
            logger.info(f'Отправлено сообщение от {from_user} в общий чат')
        response = {
            "response": '200',
            "time": time.ctime(),
            "resp_msg": 'Отправлено',
            "alert": ''
        }
        cur_user.send(pickle.dumps(response))


@server_log_config.log
def send_message_mock(msg, cur_user):
    print(f'Тестовое сообщение {msg["message"]} от пользователя {cur_user}')

@server_log_config.log
def client_available_users():
    response['response'] = '200'
    response['resp_msg'] = list(clients.values())
    return response

@server_log_config.log
def client_available_commands():
    response['response'] = '200'
    response['resp_msg'] = 'Доступные комманды:\n/quit - выход\n' \
                           '/users - список пользователей\nдля отправки сообщения конкретному' \
                           ' пользователю\nиспользуйте конструкцию ::::@USER_NAME YOUR_MESSAGE'
    return response

@server_log_config.log
def client_authenticate(msg, user):
    if not clients.get(user):
        clients[user] = msg['user']['account_name']
        print(clients)
        response['response'], response['alert'], = '200', 'Авторизация прошла успешно'
        logger.info(f'Пользователь {user} авторизован')
    else:
        response['response'], response['alert'], = '409', 'Данный пользователь уже авторизован'
        logger.warning(f'Ошибка авторизации. Повторная авторизация пользователя {user}')
    return response

if __name__ == '__main__':
    start_server()


