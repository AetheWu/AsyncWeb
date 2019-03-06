from abc import abstractmethod
import os


class BaseResponse:
    def __init__(self):
        self.head = 'HTTP/1.1 200 OK\r\n'\
        'Content-Type:text/html; charset=utf-8\r\n'\
        'Server: ZHWServer1.0\r\n'\
        'Content-Length: {length}\r\n'\
        '\n'

    @abstractmethod
    def result(self):
        raise NotImplementedError


class TextResponse(BaseResponse):
    def __init__(self, text):
        super().__init__()
        self.body = self.body_handler(text)

    def body_handler(self, text):
        if isinstance(text, str):
            return text

    def result(self):
        response = self.head.format(length=len(self.body)) + self.body
        return response.encode('utf-8')


class HTMLResponse(BaseResponse):
    def __init__(self, filepath):
        super().__init__()
        self.body_handler(filepath)

    def body_handler(self, filepath):
        try:
            with open(filepath, 'r') as f:
                self.body = f.read()

        except FileNotFoundError:
            if os.name == 'nt':
                package_path = os.path.abspath('.')
                default_path = package_path + '\\statics\\' + filepath
            elif os.name == 'linux':
                pass
            with open(default_path, 'r') as f:
                self.body = f.read()

    def result(self):
        response = self.head.format(length=len(self.body)) + self.body
        return response.encode('utf-8')


if __name__ == '__main__':
    html = HTMLResponse('index.html').result()
