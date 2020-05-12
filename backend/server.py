import sys
import bottle
from bottle import response
from json.decoder import JSONDecodeError
import datetime

from database import get_all_tasks, get_task_by_uid, add_change_task, delete_task_by_uid


app = bottle.Bottle()

class TodoItem:
    def __init__(self, description, unique_id):
        self.description = description
        self.is_completed = False
        self.uid = unique_id

    def __str__(self):
        return self.description.lower()

    def to_dict(self):
        return {
            "description": self.description,
            "is_completed": self.is_completed,
            "uid": self.uid
        }

tasks_db = {
    uid: TodoItem(desc, uid)
    for uid, desc in enumerate(
        start=1,
        iterable=[
            "прочитать книгу",
            "учиться жонглировать 30 минут",
            "помыть посуду",
            "поесть",
        ],
    )
}

useDatabase = len(sys.argv) > 1

# декоратор CORS, разрешающий доступ с любых сайтов
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        return fn(*args, **kwargs)

    return _enable_cors

@app.route("/api/message")
@enable_cors
def message():
    return {"message": "Time is " + datetime.datetime.strftime( datetime.datetime.now(), "%T" )}

@app.route("/api/tasks/", method=["GET", "POST", "OPTIONS"])
@enable_cors
def add_task():
    """
    Добавление новой задачи, либо вывод всех существующих задач
    Возврящает JSON:
    {
       tasks: [ <список с задачами, если GET, иначе tasks не будет> ]
       error: <текст ошибки, либо Null, если ошибок нет>
    }
    """
    if bottle.request.method == "OPTIONS": # заглушка, если клиент запрашивает OPTIONS
        return "OK"
    elif bottle.request.method == 'GET': # отдаем все задачи, котрорые есть
        task = []
        error = None
        if useDatabase:
           (tasks, error) = get_all_tasks()
        else:
           tasks = [task.to_dict() for task in tasks_db.values()]
        return {"tasks": tasks, "error": error }
    elif bottle.request.method == "POST": # сохраняем в базу новую задачу
        try:
            json = bottle.request.json
        except JSONDecodeError as error :
            return {"error": "json parsing error"}

        if not json:
            return {"error": "Content-Type is not json, or json is empty"}

        # desc будет всегда строкой без символов новой строки и длиной не более 64
        description = str(json.get('description', '')) \
                .replace('\n', ' ').replace('\r', '')[:64]
        # is_completed будет всегда bool
        is_completed = bool(json.get('is_completed', False))

        if len(description) == 0: # у новой задачи должно быть не пустое описание
            return {"error": "Description is empty"}

        if useDatabase: # если база данных из файла ...
            error = None
            (_, error) = add_change_task(description, is_completed)
            return {"error": error}
        else: # ... иначе база данных из оперативной памяти
            new_uid = 1
            if len(tasks_db) > 0:
                new_uid = max(tasks_db.keys()) + 1
            t = TodoItem(description, new_uid)
            t.is_completed = is_completed
            tasks_db[new_uid] = t
            return {"error": None}


@app.route("/api/tasks/<uid:int>", method=["GET", "PUT", "DELETE", "OPTIONS"])
@enable_cors
def show_or_modify_task(uid):
    """
    Изменение существующей задачи, либо ее удаление, либо просто запрос одной задачи
    Возврящает JSON:
    {
       task: {параметры задачи, если GET, иначе data не будет}
       error: <текст ошибки, либо Null, если ошибок нет>
    }
    """
    if bottle.request.method == "OPTIONS": # заглушка, если клиент запрашивает OPTIONS
        return "OK"
    elif bottle.request.method == "GET": # запрос одной задачи
        error = None
        task = None
        if useDatabase: # если база данных из файла ...
            (task, error) = get_task_by_uid(uid)
        else: # ... иначе база данных из оперативной памяти
            try:
                task = tasks_db[uid].to_dict()
            except KeyError:
                error = "uid {} not found".format(uid)

        return {"task": task, "error": error}
    elif bottle.request.method == "DELETE": # удаление задачи
        error = None
        if useDatabase: # если база данных из файла ...
            (_, error) = delete_task_by_uid(uid)
        else: # ... иначе база данных из оперативной памяти
            try:
                tasks_db.pop(uid)
            except KeyError:
                error = "uid {} not found".format(uid)
        return {"error": error}
    elif bottle.request.method == "PUT": # изменение задачи
        try:
            json = bottle.request.json
        except JSONDecodeError as error :
            return {"error": "json parsing error"}

        if not json:
            return {"error": "Content-Type is not json, or json is empty"}

        description = json.get('description', None)
        # description будет всегда строкой без символов новой строки
        # и длиной не более 64, если desc не None
        if description is not None:
            description = str(description) \
                    .replace('\n', ' ').replace('\r', '')[:64]

        is_completed = json.get('is_completed', None)
        # is_completed будет всегда bool если оно не None
        if is_completed is not None:
            is_completed = bool(is_completed)

        error = None
        if useDatabase: # если база данных из файла ...
            (_, error) = add_change_task(description, is_completed, uid)
            return {"error": error}
        else: # ... иначе база данных из оперативной памяти
            if description is not None:
                tasks_db[uid].description = description
            if is_completed is not None:
                tasks_db[uid].is_completed = is_completed
        return {"error": error}

if __name__ == "__main__":
    bottle.run(app, host="localhost", port=5000)

