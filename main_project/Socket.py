from socket import socket, AF_INET, SOCK_STREAM


class Socket(socket):

    def __init__(self):
        super(Socket, self).__init__(
            AF_INET,
            SOCK_STREAM,
        )

    def send_data(self, *args):
        raise NotImplementedError()

    def listen_socket(self, *args):
        raise NotImplementedError()

    def set_up(self):
        raise NotImplementedError

socket = Socket()
