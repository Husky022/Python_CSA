from socket import *
import time
import pickle

s = socket(AF_INET, SOCK_STREAM)
s.connect(('localhost', 7777))


def send_presence():
    return {
            "action": "presence",
            "time": time.ctime(),
            "type": "status",
            "user": {
                    "account_name":  "Tesla",
                    "status":      "Yep, I am here!"
            }
    }


def authenticate():
    return {
        "action": "authenticate",
        "time": time.ctime(),
        "user": {
                "account_name":  "Tesla",
                "password":      "CorrectHorseBatteryStaple"
            }
    }


action = authenticate()
s.send(pickle.dumps(action))
while True:
    data = pickle.loads(s.recv(1024))
    try:
        if data.get('action') == 'msg':
            print('Сообщение от %s: %s' % (data['from'], data['message']))
        else:
            print('Сообщение от сервера: ', data)
    except EOFError:
        pass