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
                    "account_name":  "Edisson",
                    "status":      "Yep, I am here!"
            }
    }


def authenticate():
    return {
        "action": "authenticate",
        "time": time.ctime(),
        "user": {
                "account_name":  "Edisson",
                "password":      "CorrectHorseBatteryStaple"
            }
    }


def quit():
    return {
        "action": "quit",
        "time": time.ctime(),
        "user": {
                "account_name":  "Edisson",
                "password":      "CorrectHorseBatteryStaple"
            }
    }


def send_to_other_client():
    return {
        "action": "msg",
        "time": time.ctime(),
        "to": "Tesla",
        "from": "Edisson",
        "message": "Привет, человечище!"
    }


# action = send_presence()
# action = authenticate()
action = send_to_other_client()
s.send(pickle.dumps(action))
data = s.recv(1024)
print('Сообщение от сервера: ', pickle.loads(data))
s.close()