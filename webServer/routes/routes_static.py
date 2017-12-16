def route_static(request):
    """
    静态资源的处理函数, 读取静态文件并生成响应返回
    """
    # 获取 request 中 file 这个key对应的value，比如 doge.gif
    filename = request.query.get('file', )
    # 拼接路径静态文件路径和静态文件名
    path = 'static/' + filename
    # 打开静态文件并HTTP响应
    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\n\r\n'
        img = header + f.read()
        return img


# 路由字典
# key 是路由(路由就是 path)
# value 是路由处理函数(就是响应)
route_dict = {}
