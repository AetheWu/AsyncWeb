import gzip

class Response:
    def __init__(self, net_source):
        print(net_source)
        self.net_source = net_source
        self.head = {}
        self.main_parse()

    def __getitem__(self, name):
        try:
            return self.head[name]
        except KeyError:
            return None

    def main_parse(self):
        head, *body = self.net_source.split(b'\r\n\r\n')

        self._head_parse(head)
        self._body_parse(body)

    def context(self):
        pass

    def _head_parse(self, head):
        head = head.decode('utf-8')

        self.response_row, *list_head = head.split('\r\n')

        list_head = [s.split(': ') for s in list_head]
        self.head = {key:val for key, val in list_head}

        self._row_parse()

    def _row_parse(self):
        try:
            protocol, status_code, *status = self.response_row.split(' ')
            self.head.update((('protocol',protocol), ('status_code', status_code), ('status', ''.join(status))))   
        except ValueError:
            pass

    def _body_parse(self, body):
        pass
