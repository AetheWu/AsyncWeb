from collections import deque
from select import select
import time
from collections import OrderedDict

from aio.event import YieldEvent

class Scheduler:
    '''
    调度器类：维护一个任务队列，任务由一个生成器组成；
    调度器负责在任务进入IO等待时进行任务切换
    '''
    def __init__(self):
        self._numtasks = 0
        self._ready = deque()
        self._read_waiting = {}
        self._write_waiting = {}
        # self.max_size = 100
        # self.link_queue = OrderedDict()

    def _iopoll(self):
        '''
        IO等待区域，使用select函数，进行IO多路复用；
        当IO事件就绪时，会调用YieldEvent.handle_resume进行IO数据处理，并恢复任务；
        :return:
        '''
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
        向任务队列新增任务；
        '''
        self._ready.append((task, None))
        self._numtasks += 1

    def add_ready(self, task, msg=None):
        '''
        将进入IO等待的任务重新加入队列，并恢复运行；
        '''
        self._ready.append((task, msg))

    def _read_wait(self, fileno, evt, task):
        self._read_waiting[fileno] = (evt, task)

    def _write_wait(self, fileno, evt, task):
        self._write_waiting[fileno] = (evt, task)

    def run(self):
        '''
        任务队列运行主函数；
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
