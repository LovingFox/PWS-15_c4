import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError


DB_PATH = "sqlite:///todos.sqlite3"
Base = declarative_base()


class Task(Base):
    """
    Описывает структуру таблицы todos для хранения записей задач
    """

    __tablename__ = "todos"

    uid = sa.Column(sa.INTEGER, primary_key=True, autoincrement=True)
    description = sa.Column(sa.TEXT, default="")
    is_completed = sa.Column(sa.BOOLEAN, default=False)

def connect_db():
    """
    Устанавливает соединение к базе данных, создает таблицы,
    если их еще нет и возвращает объект сессии 
    """
    engine = sa.create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()

def get_all_tasks():
    """
    Находит все задачи
    """
    try:
        session = connect_db()
        todos = session.query(Task).all()
    except SQLAlchemyError as e:
        return None, str(e)
    return sorted(
            [ {
                "uid": task.uid,
                "description": task.description,
                "is_completed": task.is_completed,
                } for task in todos ],
            key = lambda task: task["uid"] ), None

def get_task_by_uid(uid):
    """
    Находит задачу по идентификатору
    """
    try:
        session = connect_db()
        task = session.query(Task)\
                 .filter( Task.uid == uid )\
                 .first()
    except SQLAlchemyError as e:
        return None, str(e)
    if task:
        return { "uid": task.uid,
                 "description": task.description,
                 "is_completed": task.is_completed }, None
    else:
        return None, "uid '{}' not found".format(uid)

def add_change_task(description=None, is_completed=None, uid=None):
    """
    Добавление новой или изменение существующей задачи
    """
    try:
        session = connect_db()
        task = session.query(Task)\
                 .filter( Task.uid == uid )\
                 .first() if uid else Task() # если нет uid, то создаем новую задачу
    except SQLAlchemyError as e:
        return None, str(e)
    if not task:
        return None, "uid '{}' not found".format(uid)

    task.description = description if description != None else task.description
    task.is_completed = is_completed if is_completed != None else task.is_completed

    try:
        session.add(task)
        session.commit()
    except SQLAlchemyError as e:
        return None, str(e)
    return None, None

def delete_task_by_uid(uid):
    """
    Удаление существующей задачи по идентификатору
    """
    try:
        session = connect_db()
        task = session.query(Task)\
                 .filter( Task.uid == uid )\
                 .first()
    except SQLAlchemyError as e:
        return None, str(e)
    if not task:
        return None, "uid '{}' not found".format(uid)

    try:
        session.delete(task)
        session.commit()
    except SQLAlchemyError as e:
        return None, str(e)
    return None, None

if __name__ == "__main__":
   """
   Код для проверки работы базы данных в CLI
   """
   command = input(
         "1 - Новая задача\n" +
         "2 - Изменить задачу\n" +
         "3 - Удалить задачу\n" +
         "4 - Вывести одну задачу\n" +
         "* - Вывести все задачи\n")
   try:
      command = int(command)
   except ValueError:
      command = None

   # Добавить новую задачу
   if command == 1:
      description = None
      while not description: description = input("Описание задачи: ")

      ( _, err ) = add_change_task(description)
      print(err if err else "Задача добавлена")

   # Изменить задачу
   elif command == 2:
      uid = None
      is_completed = ""
      while not uid:
         uid = input("Идентификатор задачи: ")
         try:
            uid = int(uid)
         except:
            uid = None
      description = input("Новое описание задачи (пусто - без изменений): ")
      if not description.strip():
         description = None
      while is_completed not in (True, False, None ):
         is_completed = input("Задача сделана (y/n)? (пусто - без изменений): ")
         if not is_completed:
            is_completed = None
         elif is_completed == "y":
            is_completed = True
         elif is_completed == "n":
            is_completed = False

      ( _, err ) = add_change_task(description, is_completed, uid)
      print(err if err else "Задача изменена")

   # Удалить задачу
   elif command == 3:
      uid = None
      is_completed = ""
      while not uid:
         uid = input("Идентификатор задачи: ")
         try:
            uid = int(uid)
         except:
            uid = None

      ( _, err ) = delete_task_by_uid(uid)
      print(err if err else "Задача удалена")

   # Вывести одну задачу
   elif command == 4:
      uid = None
      is_completed = ""
      while not uid:
         uid = input("Идентификатор задачи: ")
         try:
            uid = int(uid)
         except:
            uid = None
      ( task, err ) = get_task_by_uid(uid)
      if err:
          print(err)
      elif task:
          print( "{:3} {:20} {}".format(
            task["uid"], str(task["description"]),
            "Сделано" if task["is_completed"] else "Не сделано") )
      else:
         print("Задача с идентификатором {} не найдена".format(uid))

   # Вывести все задачи
   else:
      ( tasks, err ) = get_all_tasks()
      if err:
          print(err)
      elif not tasks:
         print("Нет ни одной задачи")
      else:
         for task in tasks:
             print( "{:3} {:35} {}".format(
               task["uid"], str(task["description"]),
               "Сделано" if task["is_completed"] else "Не сделано") )
