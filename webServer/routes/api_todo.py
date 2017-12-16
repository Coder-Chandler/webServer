from utils import (
    log,
    redirect,
    json_response,
    template,
    current_user,
)
from models.todo import Todo
from models.todo import Comment
from models.user import User


# 本文件只返回 json 格式的数据
# 而不是 html 格式的数据
def all(request):
    """
    返回所有 todo
    """
    todo_list = Todo.all()
    # 要转换为 dict 格式才行
    todos = [t.json() for t in todo_list]
    return json_response(todos)


def add(request):
    """
    接受浏览器发过来的添加 todo 请求
    添加数据并返回给浏览器
    """
    currentuserid = current_user(request)
    user = User.find(currentuserid)
    log('add微博的用户以及id ', user, currentuserid)
    # 得到浏览器发送的 json 格式数据
    # 浏览器用 ajax 发送 json 格式的数据过来
    # 所以这里我们用新增加的 json 函数来获取格式化后的 json 数据
    form = request.json_loads()
    form['user_id'] = int(currentuserid)
    log('add微博的form表单 ', form)
    # 创建一个 todo
    t = Todo.new(form)
    # 把创建好的 todo 返回给浏览器
    return json_response(t.json())


def delete(request):
    """
    通过下面这样的链接来删除一个 todo
    /delete?id=1
    """
    todo_id = int(request.query.get('id'))
    t = Todo.delete(todo_id)
    return json_response(t.json())


def update(request):
    form = request.json_loads()
    todo_id = int(form.get('id'))
    t = Todo.update(todo_id, form)
    return json_response(t.json())


# 定义一个函数统一检测是否登录
def login_required(route_function):
    def func(request):
        userid = current_user(request)
        log('登录鉴定, user_id -> ', userid)
        if userid == -1:
            # 没登录 不让看 重定向到 /login
            log('检测到用户未登录，即将执行至重定向函数redirect......')
            return redirect('/login')
        else:
            # 登录了, 正常返回路由函数响应
            log('检测到用户已经登录，正常返回路由函数响应......')
            return route_function(request)

    return func


route_dict = {
    '/api/todo/all': all,
    '/api/todo/add': add,
    '/api/todo/delete': delete,
    '/api/todo/update': update,
}
