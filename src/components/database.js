import axios from 'axios';

const dataURL = 'http://localhost:5000/api/tasks/'; // адрес удаленной базы данных
const dataLocal = 'todos_db'; // имя в localStorage для локальной базы данных
const dbRemote = 'todos_type'; // имя в localStorage: false - локальная база, true - удаленная

// содержание базы данных по-умолчанию
const defaultData = [
  {
    uid: 1,
    description: 'создать вакцину от коронавируса',
    is_completed: false,
  },
  {
    uid: 2,
    description: 'получить Нобелевскую Премию',
    is_completed: false,
  },
  {
    uid: 3,
    description: 'покормить кота',
    is_completed: true,
  },
];

// записать тип базы в localStorage
function setType(remote = false) {
  localStorage.setItem(dbRemote, remote);
}

// получить из localStorage тип базы
function getType() {
  let isRemote = false;
  try {
    isRemote = JSON.parse(localStorage.getItem(dbRemote));
  } catch {
    setType();
    return false;
  }
  // Boolean(isRemote), если в isRemote будет какая-нибудь фигня после успешного JSON.parse
  return isRemote == null ? null : Boolean(isRemote);
}

// пишем задачи в localStorage
function saveData(data) {
  let dataToSave;
  data.sort((a, b) => { // сортируем перед записью список задач по uid
    if (a.uid < b.uid) return -1;
    if (a.uid > b.uid) return 1;
    return 0;
  });
  try {
    dataToSave = JSON.stringify(data);
  } catch { // если в data вдруг не json, то пишем пустой список
    dataToSave = JSON.stringify([]);
  }
  localStorage.setItem(dataLocal, dataToSave);
}

// загружаем задачи из localStorage
function loadData() {
  let data = localStorage.getItem(dataLocal);
  try {
    data = JSON.parse(data);
  } catch { // если в localStorage не json, а фигня, то содержание базы будет по-дефолту
    data = defaultData;
    saveData(data);
  }
  if (!(data instanceof Array)) { // если нашелся json, но это не список, то опять дефолт
    data = defaultData;
    saveData(data);
  }
  data = data.reduce((acc, cur) => { // фильтруем: все данные должны быть нужного типа
    if (typeof (cur.uid) === 'number'
        && typeof (cur.description) === 'string'
        && typeof (cur.is_completed) === 'boolean') {
      acc.push(cur);
    }
    return acc;
  }, []);
  return data;
}

// считываем все задачи из локальной или удаленной базы
// результатом вызываем callback(ошибка, данные_базы)
// 'ошибка' будет null, если все нормально
function getTasks(callback) {
  if (getType()) { // из удаленной
    axios.get(dataURL)
      .then((response) => {
        if (response.data.error) { // если с запросом все хорошо, но сервер вернул ошибку в данных
          callback(response.data.error);
        } else {
          callback(null, response.data.tasks);
        }
      })
      .catch((error) => {
        callback(error);
      });
  } else { // из локальной
    callback(null, loadData());
  }
}

// записываем новую задачу в локальную или удаленную базу
// descr - описание задачи, iscomp - стутус выполнения задачи
// результатом вызываем callback(ошибка)
// 'ошибка' будет null, если все нормально
function addTask(descr, iscomp, callback) {
  const requestData = {
    description: descr,
    is_completed: iscomp,
  };
  if (getType()) { // в удаленную
    axios.post(dataURL, requestData)
      .then((response) => {
        if (response.data.error) { // если с запросом все хорошо, но сервер вернул ошибку в данных
          callback(response.data.error);
        } else {
          callback();
        }
      })
      .catch((error) => {
        callback(error);
      });
  } else { // в локальную
    const data = loadData();
    // определяем макмисальный uid в базе ...
    requestData.uid = data.reduce((a, c) => (c.uid > a.uid ? c : a), {
      uid: 0, // ... по-умолчанию для .reduce фейковая задача с uid 0 ...
    }).uid + 1; // ... и прибавляем 1 для uid новой задачи
    data.push(requestData);
    saveData(data);
    callback();
  }
}

// меняем существующую задачу в локальной или удаленной базе
// uid - идентификатор существующей задачи
// descr, iscomp - новые описание и стутус выполнения задачи
// результатом вызываем callback(ошибка)
// 'ошибка' будет null, если все нормально
function changeTask(uid, descr, iscomp, callback) {
  const requestData = {
    description: descr,
    is_completed: iscomp,
  };
  if (getType()) { // в удаленной
    const todoURL = dataURL + uid;
    axios.put(todoURL, requestData)
      .then((response) => {
        if (response.data.error) { // если с запросом все хорошо, но сервер вернул ошибку в данных
          callback(response.data.error);
        }
        callback();
      })
      .catch((error) => {
        callback(null, error);
      });
  } else { // в локальной
    const data = loadData();
    // удаляем из текущего списка задач ту, котороую будем менять ...
    const newData = data.reduce((acc, cur) => {
      if (cur.uid !== uid) {
        acc.push(cur);
      } else {
        requestData.uid = uid; // ... добавляем в структур uid меняемой задачи
      }
      return acc;
    }, []);
    if (!(requestData.uid)) { // если не нашли в базе uid меняемой задачи
      callback('Error: uid '.concat(uid).concat(' not found'));
    } else {
      newData.push(requestData);
      saveData(newData);
      callback();
    }
  }
}

// удаляем существующую задачу из локальной или из удаленной базы
// uid - идентификатор существующей задачи
// результатом вызываем callback(ошибка)
// 'ошибка' будет null, если все нормально
function deleteTask(uid, callback) {
  if (getType()) { // из удаленной
    const todoURL = dataURL + uid;
    axios.delete(todoURL)
      .then((response) => {
        if (response.data.error) { // если с запросом все хорошо, но сервер вернул ошибку в данных
          callback(response.data.error);
        }
        callback();
      })
      .catch((error) => {
        callback(error);
      });
  } else { // из локальной
    const data = loadData();
    // делаем новый список задач из текущего без задачи, котороую нужно удалить
    const newData = data.reduce((acc, cur) => {
      if (cur.uid !== uid) {
        acc.push(cur);
      }
      return acc;
    }, []);
    if (data.length === newData.length) { // если не нашли задачу, которую нужно удалить
      callback('Error: uid '.concat(uid).concat(' not found'));
    } else {
      saveData(newData);
      callback();
    }
  }
}

export {
  dataLocal, dataURL, getType, setType, getTasks, addTask, changeTask, deleteTask,
};
