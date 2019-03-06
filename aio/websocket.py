from aio.event import ReadSocket,WriteSocket,AcceptSocket,YieldEvent,ConnectSocket


class Socket(object):
    def __init__(self, sock):
        self._sock = sock

    def __getattr__(self, name):
        return getattr(self._sock, name)

    def recv(self, maxbytes):
        return ReadSocket(self._sock, maxbytes)

    def send(self, response):
        return WriteSocket(self._sock, response)

    def accept(self):
        return AcceptSocket(self._sock)

    def send_file(self):
        pass

    def connect(self, addr, next_task):
        return ConnectSocket(self._sock, addr, next_task)