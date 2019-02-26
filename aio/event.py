

# This class represents a generic yield event in the scheduler
class YieldEvent:
    def handle_yield(self, sched, task):
        pass
        
    def handle_resume(self, sched, task):
        pass


# Example implementation of coroutine-based socket I/O
class ReadSocket(YieldEvent):
    def __init__(self, sock, nbytes):
        self.sock = sock
        self.nbytes = nbytes

    def handle_yield(self, sched, task):
        sched._read_wait(self.sock.fileno(), self, task)

    def handle_resume(self, sched, task):
        data = self.sock.recv(self.nbytes)
        sched.add_ready(task, data)


class WriteSocket(YieldEvent):
    def __init__(self, sock, data):
        self.sock = sock
        self.data = data

    def handle_yield(self, sched, task):
        sched._write_wait(self.sock.fileno(), self, task)

    def handle_resume(self, sched, task):
        if isinstance(self.data, str):
            self.data = self.data.encode('utf-8')

        if self.data and isinstance(self.data, bytes):
            nsent = self.sock.sendall(self.data)
            sched.add_ready(task, nsent)

        else:
            return None

class AcceptSocket(YieldEvent):
    def __init__(self, sock):
        self.sock = sock

    def handle_yield(self, sched, task):
        sched._read_wait(self.sock.fileno(), self, task)

    def handle_resume(self, sched, task):
        r = self.sock.accept()
        sched.add_ready(task, r)

class ConnectSocket(YieldEvent):
    def __init__(self, sock, addr, next_task):
        self.sock = sock
        self.addr = addr
        self.next_task = next_task

    def handle_yield(self, sched, task):
        try:
            sched._write_wait(self.sock.fileno(), self, task)
            self.sock.connect(self.addr)
        except BlockingIOError:
            pass

    def handle_resume(self, sched, task):
        sched.add_ready(task)
        sched.new(self.next_task)



