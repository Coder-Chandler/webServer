from models import Model
from models.todo import Todo


class User(Model):
    """
    User 是一个保存用户数据的 model
    现在只有两个属性 username 和 password
    """

    def __init__(self, form):
        self.id = form.get('id', None)
        self.username = form.get('username', '')
        self.password = form.get('password', '')

    def salted_password(self, password, salt='$!@><?>HUI&DWQa`'):
        # 为用户的密码'加盐'，其实就是在加密后的密码基础上再加上一段随机字符串，然后再次进行加密算法
        import hashlib
        # 定义sha256函数，接受ascii字符串，
        def sha256(ascii_str):
            return hashlib.sha256(ascii_str.encode('ascii')).hexdigest()
        # 首先用sha256加密原密码
        hash1 = sha256(password)
        # 再把加密后的愿密码加上'盐'，再进行一次加密，这样破解的成本就已经足够足够高了！
        hash2 = sha256(hash1 + salt)
        return hash2

    def hashed_password(self, pwd):
        import hashlib
        # 用 ascii 编码转换成 bytes 对象
        p = pwd.encode('ascii')
        s = hashlib.sha256(p)
        # 返回摘要字符串
        return s.hexdigest()

    def validate_register(self):
        pwd = self.password
        self.password = self.salted_password(pwd)
        if User.find_by(username=self.username) is None:
            self.save()
            return self
        else:
            return None

    def validate_login(self):
        # 传入的u这个实例包含了form，也就是登录的名字和密码，
        # 通过find_by函数比较登录输入的username和数据文件中的username，
        # 如果在数据文件中找到了登录输入的username就返回这个username，否则返货None
        u = User.find_by(username=self.username)
        # 判断是否拿到了登录的名字
        if u is not None:
            # 对比登录输入的密码和数据文件中的密码，看看是否一致，这里的salted_password是加盐的密码
            return u.password == self.salted_password(self.password)
        else:
            return False

    def todos(self):
        # 列表推倒和过滤
        # return [t for t in Todo.all() if t.user_id == self.id]
        ts = []
        for t in Todo.all():
            if t.user_id == self.id:
                ts.append(t)
        return ts

    def __repr__(self):
        return self.username
