import socket
import urllib.parse
import _thread
#
from routes.routes_static import route_static
from routes.routes_user import route_dict as user_routes
from routes.todo import route_dict as todo_routes
from routes.api_todo import route_dict as api_todo
from utils import (
    log,
    error,
)


# 定义一个 class 用于保存请求的数据
class Request(object):
    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.headers = {}
        self.cookies = {}

    def add_cookies(self):
        """
        height=169; user=gua
        """
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split('; ')
        log('cookie', kvs)
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self, header):
        """
        Accept-Language: zh-CN,zh;q=0.8
        Cookie: height=169; user=gua
        """
        # lines = header.split('\r\n')
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        self.add_cookies()

    def form(self):
        # 用法：unquote('abc%20def') -> 'abc def'
        # 把 body 通过 unquote 处理，去掉body中的 '%' 符号
        body = urllib.parse.unquote(self.body)
        # 把 body 切分，比如 'messages=goo&id=22' -> ['messages=goo', 'id=22']
        args = body.split('&')
        f = {}
        log('form debug', args, len(args))
        # 遍历 args 把每一个元素切分放进 f
        # 比如，f = {'messages': 'goo', 'id': '22'}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f

    def json_loads(self):
        """
        把 body 中的 json 格式字符串解析成 dict 或者 list 并返回
        """
        import json
        return json.loads(self.body)


def parsed_path(path):
    """
    :param: '/messages?message=hello&author=gua'
    :return:
    /messages
    {
        'message': 'hello',
        'author': 'gua',
    }
    """
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        path, query_string = path.split('?', 1)
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return path, query


def response_for_path(path, request):
    # 把 path 传入 parsed_path 函数得到一个字符串格式的path和一个字典格式的query
    path, query = parsed_path(path)
    # 把 parsed_path 函数处理过的 path 和 query 给request
    request.path = path
    request.query = query
    log('path and query', path, query, request.body)
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    # r 中都是路由函数
    r = {
        '/static': route_static,
    }
    # 注册外部的路由
    r.update(api_todo)
    r.update(user_routes)
    r.update(todo_routes)
    #
    response = r.get(path, error)
    return response(request)


def process_request(connection):
    r = connection.recv(1100)
    r = r.decode('utf-8')
    log('完整请求 -> ', r)
    log('------------------------请求结束------------------------')
    print('完整请求 -> ', r)
    print('------------------------请求结束------------------------')
    # log('ip and request, {}\n{}'.format(address, r))
    # 因为 chrome 会发送空请求导致 split 得到空 list
    # 所以这里判断一下防止程序崩溃
    if len(r.split()) < 2:
        connection.close()
    # 从浏览器的请求数据中获取请求路径（比如，'/' '/index/xxxx'
    print(r.split())
    path = r.split()[1]
    # 创建一个新的 request 并设置
    request = Request()
    # 从浏览器的请求数据中获取请求方法（GET or POST）
    request.method = r.split()[0]
    # 从浏览器的请求数据中获取headers并add给request
    request.add_headers(r.split('\r\n\r\n', 1)[0].split('\r\n')[1:])
    # 从浏览器的请求数据中获取body部分，再把 body 放入 request 中
    request.body = r.split('\r\n\r\n', 1)[1]
    # 用 response_for_path 函数来得到 path 对应的响应内容
    response = response_for_path(path, request)
    # 把响应发送给客户端
    connection.sendall(response)
    try:
        print('完整响应 -> ', response.decode('utf-8').replace('\r\n', '\n'))
        log('http响应 ->\n', response.decode('utf-8').replace('\r\n', '\n'))
        log('------------------------http响应结束------------------------')
    except Exception as e:
        log('响应异常 -> ', e)
        log('------------------------http响应结束------------------------')
    # 处理完请求, 关闭连接
    connection.close()
    print('关闭')


def run(host='', port=3000):
    """
    启动服务器
    """
    # 初始化 socket 套路
    # 使用 with 可以保证程序中断的时候正确关闭 socket 释放占用的端口
    print('start at', '{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 监听 接受 读取请求数据 解码成字符串
        s.listen(3)
        # 无限循环来处理请求
        while True:
            connection, address = s.accept()
            print('连接成功, 使用多线程处理请求', address)
            # 开一个新的线程来处理请求, 第二个参数是传给新函数的参数列表, 必须是 tuple
            # tuple 如果只有一个值 必须带逗号
            _thread.start_new_thread(process_request, (connection,))


if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='',
        port=3000,
    )
    """
    解释：**config
    **config的知识来自（**kwargs，*args）就是所说的关键字参数和被关键字参数，程序说明
    def log(*args, **kwargs):
        print('args',args)
        print('kwargs',kwargs)
    log(1,2,3,4) ---> args:(1,2,3,4), kwargs:{}
    log(1,[1,2], c=1) ---> args:(1,[1,2]), kwargs:{'c':4}
    这里的run(**config)，上面函数是run(host='', port=3000)那么也就是指{'host':'', 'port':3000}
    """
    run(**config)

"""

HTTP请求过程
1.
POST /messages?messages=goo&id=22 HTTP/1.1
Content-Type: application/json
Content-Length: 18
......

messages=goo&id=22

2.
HTTP1.1 302 ok
Location: /messages
....

3.
GET /messages HTTP/1.1
Host: .....

4.
HTTP 200 ok
Content-Type: text/html
Content-Length: ...

<html>
    ....
</html>

5.
浏览器把新的页面显示出来
"""

