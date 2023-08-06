class BaseException(Exception):
    pass


class ServiceNotFound(BaseException):
    def __init__(self, service):
        self.service = service

    def __str__(self):
        return str(self.service)


class RemoteException(BaseException):
    pass
