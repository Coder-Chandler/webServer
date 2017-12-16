var timeString = function(timestamp) {
    t = new Date(timestamp * 1000)
    t = t.toLocaleTimeString()
    return t
}

var commentsTemplate = function(comments) {
    var html = ''
    for(var i = 0; i < comments.length; i++) {
        var c = comments[i]
        var t = `
            <div>
                ${c.content}
            </div>
        `
        html += t
    }
    return html
}

var todoTemplate = function(todo) {
    var title = todo.title
    var id = todo.id
    var comment = commentsTemplate(todo.comments)
    var ut = timeString(todo.ut)
    // data-xx 是自定义标签属性的语法
    // 通过这样的方式可以给任意标签添加任意属性
    // 假设 d 是 这个 div 的引用
    // 这样的自定义属性通过  d.dataset.xx 来获取
    // 在这个例子里面, 是 d.dataset.id
    var t = `
        <div class="todo-cell" id='todo-${id}' data-id="${id}">
            <span class='todo-title'>${title}</span>
            <time class='todo-ut'>${ut}</time>
            <button class="todo-edit">编辑</button>
            <button class="todo-delete">删除</button>
            <div class="comment-list">
                评论：
                ${comment}
            </div>
            <div class="comment-form">
                <input type="hidden" name="todo_id" value="">
                <input id='comment-input' name="content">
                <br>
                <button id="comment-add-button">添加评论</button>
            </div>
        </div>
    `
    return t
    /*
    上面的写法在 python 中是这样的
    t = """
    <div class="todo-cell">
        <button class="todo-delete">删除</button>
        <span>{}</span>
    </div>
    """.format(todo)
    */
}

var insertTodo = function(todo) {
    //
    var todoCell = todoTemplate(todo)
    // 插入 todo-list
    var todoList = e('.todo-list')
    todoList.insertAdjacentHTML('beforeend', todoCell)
}

var insertEditForm = function(cell) {
    var form = `
        <div class='todo-edit-form'>
            <input class="todo-edit-input">
            <button class='todo-update'>更新</button>
        </div>
    `
    cell.insertAdjacentHTML('beforeend', form)
}

var loadTodos = function() {
    // 调用 ajax api 来载入数据
    apiTodoAll(function(r) {
        // console.log('load all', r)
        // 解析为 数组
        var todos = JSON.parse(r)
        // 循环添加到页面中
        for(var i = 0; i < todos.length; i++) {
            var todo = todos[i]
            insertTodo(todo)
        }
    })
}

var bindEventTodoAdd = function() {
    //通过函数 e 抓取到 <button id='id-button-add'>add</button> 中的 id-button-add
    var b = e('#id-button-add')
    // 注意, 第二个参数可以直接给出定义函数
    b.addEventListener('click', function(){
        ////通过函数 e 抓取到 <input id='id-input-todo'> 中的 id-input-todo
        var input = e('#id-input-todo')
        //拿到input框中用户输入的数据字段
        var title = input.value
        //打印出用户输入的数据字段
        log('click add', title)
        //设置form表单
        var form = {
            'title': title,
        }
        //调用 apiTodoAdd 函数异步加载数据
        apiTodoAdd(form, function(r) {
            log('form 表单 ', form)
            // 收到返回的数据, 插入到页面中
            var todo = JSON.parse(r)
            log('todo ', todo)
            log('todo的用户id ', todo.user_id)
            insertTodo(todo)
            // if (todo.user_id > -1){
            //     //调用 insertTodo 函数插入todo数据
            //     insertTodo(todo)
            // }
            // else {
            //     window.location.href="http://localhost:3000/login"
            // }

        })
    })
}

var bindEventTodoDelete = function() {
    var todoList = e('.todo-list')
    // 注意, 第二个参数可以直接给出定义函数
    todoList.addEventListener('click', function(event){
        var self = event.target
        if(self.classList.contains('todo-delete')){
            // 删除这个 todo
            var todoCell = self.parentElement
            var todo_id = todoCell.dataset.id
            apiTodoDelete(todo_id, function(r){
                log('删除成功', todo_id)
                todoCell.remove()
            })
        }
    })
}

var bindEventTodoEdit = function() {
    var todoList = e('.todo-list')
    // 注意, 第二个参数可以直接给出定义函数
    todoList.addEventListener('click', function(event){
        var self = event.target
        if(self.classList.contains('todo-edit')){
            // 删除这个 todo
            var todoCell = self.parentElement
            insertEditForm(todoCell)
        }
    })
}

var bindEventTodoUpdate = function() {
    var todoList = e('.todo-list')
    // 注意, 第二个参数可以直接给出定义函数
    todoList.addEventListener('click', function(event){
        var self = event.target
        if(self.classList.contains('todo-update')){
            log('点击了 update ')
            //
            var editForm = self.parentElement
            // querySelector 是 DOM 元素的方法
            // document.querySelector 中的 document 是所有元素的祖先元素
            var input = editForm.querySelector('.todo-edit-input')
            var title = input.value
            // 用 closest 方法可以找到最近的直系父节点
            var todoCell = self.closest('.todo-cell')
            var todo_id = todoCell.dataset.id
            var form = {
                'id': todo_id,
                'title': title,
            }
            log('form', form)
            apiTodoUpdate(form, function(r){
                log('更新成功', todo_id)
                var todo = JSON.parse(r)
                var selector = '#todo-' + todo.id
                log('selector', selector)
                var todoCell = e(selector)
                log('todoCell', todoCell)
                var titleSpan = todoCell.querySelector('.todo-title')
                log('titleSpan', titleSpan)
                titleSpan.innerHTML = todo.title
//                todoCell.remove()
            })
        }
    })
}


var bindEvents = function() {
    //增加一条todo
    bindEventTodoAdd()
    //删除一条todo
    bindEventTodoDelete()
    //编辑一条tudo
    bindEventTodoEdit()
    //更新一条todo
    bindEventTodoUpdate()
}


var __main = function() {
    //绑定事件的函数
    bindEvents()
    //加载todo数据的函数
    loadTodos()
}


//函数主入口
__main()