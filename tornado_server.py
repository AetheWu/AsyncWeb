import tornado.web
import tornado.ioloop

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello, tornado')

def make_app():
    return tornado.web.Application([
        (r'/', IndexHandler),
    ]
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    print('web run')
    tornado.ioloop.IOLoop.current().start()