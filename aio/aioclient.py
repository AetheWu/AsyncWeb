import socket
import ssl
import gzip
import re
from urllib import request
from unicodedata import normalize

from aio.event import ReadSocket
from aio.websocket import Socket
from aio.parse_response import Response


class HttpClient:
    def get(self, url:str, **kwargs):
        '''
        异步http get请求任务，请求为非阻塞；
        '''
        try:
            sock, host, port, request = self.request(url, method='GET', data=None, **kwargs)
            sock.setblocking(False)
            self.client = Socket(sock)
            print('get:', url)
            yield self.client.connect((host, port), self.handle_request(request))

        except ConnectionError:
            print('Connection error')
            self.client.close()

    def post(self, url, form, **kwargs):
        pass  

    def handle_request(self, request):
        yield from self._send(request)
        list_response = []
        while True:
            response = yield self.client.recv(1024)
            if not response:
                break
            list_response.append(response)

        response = b''.join(list_response)
        print(response)

    def request(self, url, method, data=None, **kwargs):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        host, port, path = self._url_parse(url)

        if port == '443':
            sock = ssl.wrap_socket(sock)

        self._init_head(host, path, method)
        self.head.update(kwargs)

        if data:
            body = '\r\n' + '&'.join(['='.join((k,data[k])) for k in data])
            request = self._head2str() + body
        else:
            request = self._head2str()

        return sock, host, port, request

    def block_get(self, url, **kwargs):
        sock, host, port, request = self.request(url, method='GET', **kwargs)

        sock.connect((host, port))
        sock.send(request.encode('utf-8'))
        data = sock.recv(1024)

        response = []
        while data:
            response.append(data)
            data = sock.recv(1024)

        result = b''.join(response)
        response = Response(result)
        print(response.head)

    def _url_parse(self, url):
        rel = request.urlparse(url)
        if not rel.netloc:
            print('error url')
            raise TypeError
        ip = rel.netloc

        if rel.scheme == 'https': 
            port = 443
        else:
            port = 80

        if rel.path:
            path = rel.path
        else:
            path = '/'

        print(ip, port ,path)
        return (ip, port, path)
    
    def _init_head(self, host, path, method):
        self.head = {}
        self.head.update({'Host':' '+host})
        self.head.update({'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
        self.head.update({'User-Agent':'Chrome/72.0.3626.119 Safari/537.36'})
        self.head.update({'Accept-Encoding':'gzip, br'})
        self.head.update({'Connection':'close'})

        self.line = '{method} {path} HTTP/1.1\r\n'.format(method=method,path=path)

    def _head2str(self):
        list_req = [':'.join((url, text)) for url, text in self.head.items()]
        list_req.append('\r\n')

        str_request = '\r\n'.join(list_req)
        
        return self.line + str_request

    def _send(self, request):
        try:
            yield self.client.send(request)
        except ConnectionError:
            print('Send error')

    def _recv(self):
        response = yield self.client.recv(1024)
        return response

if __name__ == '__main__':
    # url = 'https://www.runoob.com/python3/python3-tutorial.html'
    url = 'http://127.0.0.1/'
    # url = 'https://cn.bing.com/translator/'
    cli = HttpClient()
    cli.block_get(url)