import re
import json
from collections import defaultdict
from collections import Mapping

REQUEST_LINE = re.compile(r'(GET|POST)[^\r\n]+', flags=re.I)

class RequestParser(Mapping):
    def __init__(self, req_source):
        self.req = {}

        self._req_source = req_source
        self._main_parse()

    def __getitem__(self, key):
        try:
            return self.req.__getitem__(key)
        except KeyError:
            return self.__missing__(key)

    def __len__(self):
        return len(self.req)

    def __iter__(self):
        return iter(self.req)

    def __missing__(self, key):
        return None

    def _main_parse(self):
        try:
            self._req_line_loads()
            self._req_head_loads()
            # self.req = json.dumps(self.req)
        except ValueError:
            print('error')

    def _req_line_loads(self):
        if self._req_source is None:
            return None

        request_line = re.search(REQUEST_LINE, self._req_source)
        if request_line:
            req_method, req_url, req_protocol = re.split(r'\s+', request_line.group())
            self.req.update({'method':req_method})
            self.req.update({'url':req_url})
            self.req.update({'protocol':req_protocol})

    def _req_head_loads(self):
        HOST_RE = re.compile(r'(?<=host:\s)[^\r\n]+', flags=re.I)
        CONN_RE = re.compile(r'(?<=connection:\s)[^\r\n]+', flags=re.I)
        USER_RE = re.compile(r'(?<=User-Agent:\s)[^\r\n]+', flags=re.I)

        
        host = re.search(HOST_RE, self._req_source)
        conn = re.search(CONN_RE, self._req_source)
        user_agent = re.search(USER_RE, self._req_source)

        if host:
            self.req.update({'host':host.group()})

        if conn:
            self.req.update({'connection':conn.group()})

        if user_agent:
            self.req.update({'user_agent':user_agent.group()})


if __name__ == '__main__':
    req_source = 'GET / HTTP/1.1\r\nHost: 127.0.0.1:16000\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\nCookie: csrftoken=joP1Gzf0mSJGctyBjN0XqEb3ip9IC8mDhRg4iyOV4ySGwesMnxlc4547bUBOiB6G\r\n\r\n'
    # print(req_source)
    req = RequestParser(req_source)
    print(req['hello'])