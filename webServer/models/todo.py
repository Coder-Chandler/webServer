import time
from models import Model


# 针对我们的数据 TODO
# 做 4 件事情
"""
C create 创建数据
R read 读取数据
U update 更新数据
D delete 删除数据

Todo.new() 来创建一个 todo
"""


class Todo(Model):
    # @classmethod
    # def new(cls, form):
    #     """
    #     创建并保存一个 todo 并且返回它
    #     Todo.new({'title': '吃饭'})
    #     :param form: 一个字典 包含了 todo 的数据
    #     :return: 创建的 todo 实例
    #     """
    #     # 下面一行相当于 t = Todo(form)
    #     t = cls(form)
    #     t.save()
    #     return t

    @classmethod
    def update(cls, id, form):
        t = cls.find(id)
        valid_names = [
            'title',
            'completed'
        ]
        for key in form:
            # 这里只应该更新我们想要更新的东西
            if key in valid_names:
                setattr(t, key, form[key])
        # 更新修改时间
        t.ut = int(time.time())
        t.save()
        return t

    @classmethod
    def complete(cls, id, completed=True):
        """
        用法很方便
        Todo.complete(1)
        Todo.complete(2, False)
        """
        t = cls.find(id)
        t.completed = completed
        t.save()
        return t

    def json(self):
        d = self.__dict__.copy()
        comments = [c.json() for c in self.comments()]
        d['comments'] = comments
        return d

    def comments(self):
        return Comment.find_all(todo_id=self.id)

    def __init__(self, form):
        self.id = None
        self.title = form.get('title', '')
        self.user_id = int(form.get('user_id', -1))
        # 下面的是默认的数据
        self.completed = False
        # ct ut 分别是 created_time  updated_time
        # 创建时间 和 更新时间
        self.ct = int(time.time())
        self.ut = self.ct


# 评论类
class Comment(Model):

    @classmethod
    def update(cls, id, form):
        t = cls.find(id)
        valid_names = [
            'content',
            'completed'
        ]
        for key in form:
            # 这里只应该更新我们想要更新的东西
            if key in valid_names:
                setattr(t, key, form[key])
        # 更新修改时间
        t.ut = int(time.time())
        t.save()
        return t

    def __init__(self, form):
        self.id = None
        self.user_id = None
        self.content = form.get('content', '')
        # 和别的数据关联的方式, 用 user_id 表明拥有它的 user 实例
        self.todo_id = int(form.get('todo_id', -1))
