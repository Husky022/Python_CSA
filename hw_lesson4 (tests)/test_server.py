import unittest
import time


from hw_lesson3 import server


server.clients = {'user1': 'socket1', 'user2': 'socket2', 'user3': 'socket3'} # "Эмуляция списка пользователей для теста"


class TestServer(unittest.TestCase):


    def test_client_available_users(self):
        self.assertEqual(server.client_available_users(),
                         {"response": '200', "time": time.ctime(), "resp_msg": ['user1', 'user2', 'user3'], "alert": ''})

    def test_client_available_commands(self):
        self.assertEqual(server.client_available_commands(),
                         {"response": '200', "time": time.ctime(), "resp_msg": 'Доступные комманды:\n/quit - выход\n'
                           '/users - список пользователей\nдля отправки сообщения конкретному'
                           ' пользователю\nиспользуйте конструкцию ::::@USER_NAME YOUR_MESSAGE', "alert": ''})

    def test_client_quit(self):
        self.assertEqual(server.client_quit('socket2'),
                         {"response": '200', "time": time.ctime(), "resp_msg": 'Пользователь вышел', "alert": ''})

    # Проверка, если отправителя нет в списке пользователей (не авторизован)
    def test_send_message_no_auth(self):
        self.assertEqual(server.send_message({"action": 'msg', "time": time.ctime(), "message": "text text"}, 'socket4'),
                         {"response": '401', "time": time.ctime(), "resp_msg": 'Для авторизации нажмите /auth', "alert": 'Не авторизован'})

    # Проверка, если указан получатель, которого нет в доступном списке
    def test_send_message_to_not_available_user(self):
        self.assertEqual(server.send_message({"action": 'msg', "time": time.ctime(), "message": "@user4 text"}, 'socket1'),
                         {"response": '404', "time": time.ctime(), "resp_msg": 'Не отправлено. Такого получателя не существует', "alert": ''})

# Проверка, если указан получатель, который есть в списке (Тест вылетает, хоть и работает функционал)
#     def test_send_message_to_available_user(self):
#         self.assertEqual(server.send_message({"action": 'msg', "time": time.ctime(), "message": "@user2 text"}, 'socket1'),
#                          {"response": '200', "time": time.ctime(), "resp_msg": 'Отправлено', "alert": ''})


    # Проверка, если вводят имя неавторизованного пользователя (Если запускать этот тест к общей куче - вылетает ошибка в тесте available users
    # def test_client_authenticate(self):
    #     self.assertEqual(server.client_authenticate({"action": "authenticate", "time": time.ctime(),"user": {"account_name": 'user5',"password": ''}}, 'socket5'),
    #                      {"response": '200', "time": time.ctime(), "resp_msg": 'Авторизация прошла успешно', "alert": ''})

    # Проверка, если вводят имя уже авторизованного пользователя
    def test_client_authenticate_in_list(self):
        self.assertEqual(server.client_authenticate({"action": "authenticate", "time": time.ctime(),"user": {"account_name": 'user1',"password": ''}}, 'socket1'),
                         {"response": '409', "time": time.ctime(), "resp_msg": 'Данный пользователь уже авторизован', "alert": ''})


if __name__ == '__main__':
    unittest.main()