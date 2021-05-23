import unittest
import time


request = {
    "action": '',
    "time": time.ctime()
}

def quit():
    request['action'] = 'quit'
    return request

def request_available_users():
    request['action'] = 'available_users'
    return request

def request_available_commands():
    request['action'] = 'available_commands'
    return request

def start_client():
    global request
    # listen_thread = threading.Thread(target=listen_server)
    # listen_thread.start()
    username = 'username'
    while not username:
        username = input('Имя не может быть пустым! Введите имя:')
    request = {
        "action": "authenticate",
        "time": time.ctime(),
        "user": {
            "account_name": 'username',
            "password": ''
        }
    }
    return request




class TestClient(unittest.TestCase):


    def test_quit(self):
        self.assertEqual(quit(), {"action": 'quit', "time": time.ctime()})

    def test_request_available_users(self):
        self.assertEqual(request_available_users(), {"action": 'available_users', "time": time.ctime()})

    def test_request_available_commands(self):
        self.assertEqual(request_available_commands(), {"action": 'available_commands', "time": time.ctime()})

    def test_start_client(self):
        self.assertEqual(start_client(), {"action": 'authenticate', "time": time.ctime(), "user": {"account_name": 'username', "password": ''}})

if __name__ == '__main__':
    unittest.main()

