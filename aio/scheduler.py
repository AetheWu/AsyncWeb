from collections import deque
from select import select
import time
from collections import OrderedDict

from aio.event import YieldEvent

class Scheduler:
    def __init__(self):
        self._numtasks = 0       # Total num of tasks
        self._ready = deque()    # Tasks ready to run
        self._read_waiting = {}  # Tasks waiting to read
        self._write_waiting = {} # Tasks waiting to write
        self.max_size = 100
        self.link_queue = OrderedDict()

    # Poll for I/O events and restart waiting tasks
    def _iopoll(self):
        rset,wset,_ = select(self._read_waiting,
                                self._write_waiting,[])
        for r in rset:
            evt, task = self._read_waiting.pop(r)
            evt.handle_resume(self, task)
        for w in wset:
            evt, task = self._write_waiting.pop(w)
            evt.handle_resume(self, task)

    def new(self,task):
        '''
        Add a newly started task to the scheduler
        '''
        self._ready.append((task, None))
        self._numtasks += 1

    def add_ready(self, task, msg=None):
        '''
        Append an already started task to the ready queue.
        msg is what to send into the task when it resumes.
        '''
        self._ready.append((task, msg))

    # Add a task to the reading set
    def _read_wait(self, fileno, evt, task):
        self._read_waiting[fileno] = (evt, task)
                
    def _link_buffer(self, fileno, evt, task):
        self.link_queue[fileno] = (evt, task)

    # Add a task to the write set
    def _write_wait(self, fileno, evt, task):
        self._write_waiting[fileno] = (evt, task)

    def run(self):
        '''
        Run the task scheduler until there are no tasks
        '''
        while self._numtasks:
            try:
                if not self._ready:
                    self._iopoll()
                task, msg = self._ready.popleft()
                try:
                    # Run the coroutine to the next yield
                    r = task.send(msg)
                    if isinstance(r, YieldEvent):
                        r.handle_yield(self, task)
                    else:
                        raise RuntimeError('unrecognized yield event')
                except StopIteration:
                    self._numtasks -= 1
            except ConnectionError:
                pass
