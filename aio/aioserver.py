import os
import sys
import time
from select import select
from collections import deque
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from aio.scheduler import Scheduler
from aio.request import RequestParser
from aio.urls import urls
from aio.websocket import Socket

def readline(sock):
    c = yield sock.recv(1024)
    if c is not None:
        return c.decode('utf-8')


#async web server using generators
class AIOServer:
    def  __init__(self,addr,sched):
        self.sched = sched
        sched.new(self.server_loop(addr))

    def server_loop(self,addr):
        s = Socket(socket(AF_INET,SOCK_STREAM))
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(5)
        while True:
            c,a = yield s.accept()
            print('Got connection from ', a)
            self.sched.new(self.client_handler(Socket(c)))

    def client_handler(self,client):
        while True:
            line = yield from readline(client)
    
            if line is not None:
                request = self._request_handler(line)
                response = self._response_handler(request)
                if response is None or not hasattr(response, 'result'):
                    return None
                yield client.send(response.result())
            else:
                break
     
        client.close()
        print('client close')

    def _request_handler(self, line):
        return RequestParser(line)

    def _response_handler(self, request):
        if not isinstance(request, RequestParser):
            raise TypeError('request type error')
        
        url = request['url']

        for _url in urls:
            if (url is not None) and (_url['url'] == url):
                return _url['view'](request)

        return None


def main():
    if len(sys.argv) >= 2:
        port = sys.argv[1]
        if port.isdigit():
            port = int(port)

    else:
        port = 16000

    addr = '127.0.0.1'   
    print('HTTPserver run in {}:{}'.format(addr, port))  
    
    sched = Scheduler()
    AIOServer((addr, port), sched)
    sched.run()


if __name__ == '__main__':
    # print(os.path.abspath(''))
    main()