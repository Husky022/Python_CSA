class VerifyMeta(type):
    def __init__(self, clsname, bases, clsdict):
        print(clsdict)
        for key, value in clsdict.items():
            if hasattr(key, "send_data"):
                raise TypeError('Ошибочка')

        type.__init__(self, clsname, bases, clsdict)

class ClientVerifier(metaclass=VerifyMeta):
    pass


class ServerVerifier(metaclass=VerifyMeta):
    pass

