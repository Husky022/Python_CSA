from socket import socket, AF_INET, SOCK_STREAM


class VerifyMeta(type):
    def __init__(self, clsname, bases, clsdict):
        print(clsdict)
        for key, value in clsdict.items():
            if hasattr(key, "send_data"):
                raise TypeError('Ошибочка')

        type.__init__(self, clsname, bases, clsdict)


class Socket(socket, metaclass=VerifyMeta):

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
