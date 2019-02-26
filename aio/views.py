from aio.response import TextResponse, HTMLResponse

'''return view instance or callable func through the url'''

def index(request):
    path = 'index.html'
    return HTMLResponse(path)

def hello(request):
    body = 'hello, ' + request['host']
    return TextResponse(body)
