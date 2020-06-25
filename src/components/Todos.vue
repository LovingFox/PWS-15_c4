<template>
  <div>
    <h2>Задачи базы данных {{ dbCurrent }}</h2>
    <h5>Выполнено: {{ todosCountDone }}; Осталось: {{ todosCountNotDone }};
      Всего: {{ this.todos.length }}</h5>
    <statusinfo
      :message="statusMessage"
      :variant="statusType"
      :showIt="showStatus"
      @stop="stopStatus"
      @clear="clearStatus">
    </statusinfo>
    <div class="btn-group float-left">
      <button type="button"
              id="task-add"
              class="btn btn-success btn-sm"
              v-b-modal.todo-update-modal
              @click="updatePrepare()">
        Добавить задачу
      </button>
      <button type="button"
              id="task-add"
              class="btn btn-success btn-sm"
              v-b-modal.change-database-modal>
        Выбрать базу данных
      </button>
    </div>
    <table class="table table-dark table-stripped table-hover">
      <thead class="thead-light">
      <tr>
        <th>Uid</th>
        <th>Описание</th>
        <th>Статус</th>
        <th>Действие</th>
      </tr>
      </thead>
      <tbody>
        <tr v-for="(todo, index) in todos" :key="index">
          <td>{{ todo.uid }}</td>
          <td>{{ todo.description }}</td>
          <td>
            <span v-if="todo.is_completed">Выполнено</span>
            <span v-else>Не выполнено</span>
          </td>
          <td>
            <div class="btn-group" role="group">
              <button type="button"
                class="btn btn-secondary btn-sm"
                v-b-modal.todo-update-modal
                @click="updatePrepare(todo)">
                Обновить
              </button>
              &nbsp;
              <button type="button"
                class="btn btn-danger btn-sm"
                v-b-modal.todo-delete-modal
                @click="deleteTodo(todo)">
                Удалить
              </button>
            </div>
          </td>
        </tr>
        </tbody>
    </table>
    <!-- Модальное окно для выбора базы данных -->
    <!-- Вызывается автоматически, если база не выбрана, либо по кнопке выбора базы данных -->
    <b-modal ref="changeDatabaseModal"
             id="change-database-modal"
             title="Выбрать базу данных"
             hide-footer>
      <b-form @submit="onChangeDatabase" @reset="onChangeDatabaseReset" class="w-100">
      <b-form-group>
        <b-form-radio v-model="dbType" value="false">{{ dbLocal }}</b-form-radio>
        <b-form-radio v-model="dbType" value="true">{{ dbRemote }}</b-form-radio>
      </b-form-group>
      <b-button-group>
        <b-button type="submit" variant="primary">Выбрать</b-button>
        <b-button type="reset" variant="danger">Отмена</b-button>
      </b-button-group>
      </b-form>
    </b-modal>
    <!-- Модальное окно ввода данных задачи -->
    <!-- Вызывается по кнопке добавления задачи, либо по кнопке изменения задачи -->
    <b-modal ref="updateTodoModal"
             id="todo-update-modal"
             :title="updateTodoForm.title"
             hide-footer>
      <b-form @submit="updateTodoForm.func" @reset="onUpdateReset" class="w-100">
      <b-form-group id="form-update-description-group"
                    label="Описание:"
                    label-for="form-update-description-input">
        <b-form-input id="form-update-description-input"
                      type="text"
                      v-model="updateTodoForm.description"
                      required>
        </b-form-input>
      </b-form-group>
      <b-form-group id="form-update-complete-group">
        <b-form-checkbox-group v-model="updateTodoForm.is_completed" id="form-update-checks">
          <b-form-checkbox value="true">Задача выполнена?</b-form-checkbox>
        </b-form-checkbox-group>
      </b-form-group>
      <b-button-group>
        <b-button type="submit" variant="primary">{{ updateTodoForm.buttonText }}</b-button>
        <b-button type="reset" variant="danger">Отмена</b-button>
      </b-button-group>
      </b-form>
    </b-modal>
    <!-- Модальное окно подтверждения удаления задачи -->
    <!-- Вызывается по кнопке удаления задачи -->
    <b-modal ref="deleteTodoModal"
             id="todo-delete-modal"
             :title="updateTodoForm.title"
             hide-footer>
      <h3>{{ updateTodoForm.description }}</h3>
      <b-form @submit="onDeleteSubmit" @reset="onDeleteReset" class="w-100">
      <b-button-group>
        <b-button type="submit" variant="danger">Удалить</b-button>
        <b-button type="reset" variant="primary">Отмена</b-button>
      </b-button-group>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import StatusInfo from './Status.vue';
import {
  // переменная базы в localStorage, и url к API удаленной базе данных
  dataLocal, dataURL,
  // функции работы с базой данных, одинаковы для локальной и удаленной
  getType, setType, getTasks, addTask, changeTask, deleteTask,
} from './database';

export default {
  name: 'Todos',
  data() {
    return {
      todos: [], // список задач
      updateTodoForm: { // структура для создания/обновления/удаления задачи модального окна
        uid: 0,
        description: '',
        is_completed: [], // чекбокс выполнена задача или нет
        title: '', // название модального окна
        buttonText: '', // текст на кнопке
        func: undefined, // функция, вызываемая по нажатию на кнопку buttonText
      },
      statusMessage: '', // сообщение для всплывающего статуса
      statusType: '', // тип подсветки сообщения статуса
      showStatus: false, // true/false показывать/не_показывать статус
      dbRemote: dataURL, // храним переменную с url к удаленной базе (для текста в форме и в шапке)
      // храним переменную базы в localStorage (для текста в форме и в шапке)
      dbLocal: 'localStorage('.concat(dataLocal).concat(')'),
      dbType: false, // true/false: используется удаленная/локальная база
    };
  },
  methods: {
    // скрываем всплывающее сообщение статус
    clearStatus() {
      this.showStatus = false;
    },
    // останавливаем скрытие статуса по таймеру
    stopStatus() {
      this.showStatus = true;
    },
    // показываем статус с ошибкой
    statusError(message) {
      this.statusMessage = message;
      this.statusType = 'danger';
      this.showStatus = true;
    },
    // показываем инфо-статус, скроется сам через 2 сек.
    statusSuccess(message) {
      this.statusMessage = message;
      this.statusType = 'success';
      this.showStatus = 2;
    },
    // показываем статус с предупреждением
    statusWarn(message) {
      this.statusMessage = message;
      this.statusType = 'warning';
      this.showStatus = true;
    },
    // подготавливаем данные для формы модального окна
    // по нажатию кнопки добавления/изменения задачи
    updatePrepare(todo = null) {
      if (todo == null) { // нажата кнопка добавления задачи
        this.updateTodoForm.uid = 0;
        this.updateTodoForm.is_completed = [];
        this.updateTodoForm.description = '';
        this.updateTodoForm.title = 'Добавить задачу';
        this.updateTodoForm.buttonText = 'Добавить';
        this.updateTodoForm.func = this.onAddSubmit;
      } else { // нажата кнопка изменения задачи
        this.updateTodoForm.uid = todo.uid;
        this.updateTodoForm.is_completed = todo.is_completed ? [true] : [];
        this.updateTodoForm.description = todo.description;
        this.updateTodoForm.title = 'Обновить задачу '.concat(todo.uid);
        this.updateTodoForm.buttonText = 'Обновить';
        this.updateTodoForm.func = this.onUpdateSubmit;
      }
    },
    // подготавливаем данные для модального окна подтверждения удаления задачи
    deleteTodo(todo) {
      this.updateTodoForm.uid = todo.uid;
      this.updateTodoForm.description = todo.description;
      this.updateTodoForm.title = 'Удалить задачу '.concat(todo.uid).concat('?');
    },
    // обновляем список задач запросом к базе данных
    getTodos() {
      // запрос к базе данных
      getTasks((error, data) => {
        if (error) {
          this.statusError(error);
          this.todos = [];
        } else {
          this.todos = data;
        }
      });
    },
    // добавляем новую задачу по нажатию кнопки модального окна
    onAddSubmit(event) {
      event.preventDefault();
      this.$refs.updateTodoModal.hide();
      this.statusWarn('Добавление задачи, пожалуйста, подождите...');
      // запрос к базе данных
      addTask(this.updateTodoForm.description,
        this.updateTodoForm.is_completed.length > 0,
        (error) => {
          if (error) {
            this.statusError(error);
          } else {
            this.statusSuccess('Задача "'.concat(this.updateTodoForm.description).concat('" добавлена'));
            this.getTodos(); // обновляем список задач
          }
        });
    },
    // обновляем существующую задачу по нажатию кнопки модального окна
    onUpdateSubmit(event) {
      event.preventDefault();
      this.$refs.updateTodoModal.hide();
      this.statusWarn('Обновление задачи, пожалуйста, подождите...');
      // запрос к базе данных
      changeTask(this.updateTodoForm.uid,
        this.updateTodoForm.description,
        this.updateTodoForm.is_completed.length > 0,
        (error) => {
          if (error) {
            this.statusError(error);
          } else {
            this.statusSuccess('Задача uid '.concat(this.updateTodoForm.uid).concat(' обновлена'));
            this.getTodos(); // обновляем список задач
          }
        });
    },
    // удаляем существующую задачу по нажатию кнопки модального окна
    onDeleteSubmit(event) {
      event.preventDefault();
      this.$refs.deleteTodoModal.hide();
      this.statusWarn('Удаление задачи, пожалуйста, подождите...');
      // запрос к базе данных
      deleteTask(this.updateTodoForm.uid,
        (error) => {
          if (error) {
            this.statusError(error);
          } else {
            this.statusSuccess('Задача uid '.concat(this.updateTodoForm.uid).concat(' удалена'));
            this.getTodos(); // обновляем список задач
          }
        });
    },
    // меняем базу данных по нажатию кнопки модального окна
    onChangeDatabase(event) {
      event.preventDefault();
      this.$refs.changeDatabaseModal.hide();
      if (this.dbType !== null) { // если радио-кнопка выбрана
        setType(this.dbType); // пишем в localStorage тип базы данных (true/false)
        this.statusSuccess('Выбрана база данных '.concat(this.dbCurrent));
        this.getTodos(); // обновляем список задач выбранной базы данных
      }
    },
    // нажата кнопка отмены удаления задачи в модальном окне
    onDeleteReset(event) {
      event.preventDefault();
      this.$refs.deleteTodoModal.hide();
    },
    // нажата кнопка отмены добавления/удаления задачи в модальном окне
    onUpdateReset(event) {
      event.preventDefault();
      this.$refs.updateTodoModal.hide();
    },
    // нажата кнопка отмены выбора базы данных в модальном окне
    onChangeDatabaseReset(event) {
      event.preventDefault();
      this.$refs.changeDatabaseModal.hide();
    },
    // проверка, выбрана ли база данных
    checkDatabaseSelected() {
      this.dbType = getType();
      if (this.dbType == null) { // если база данных не выбрана ...
        this.$refs.changeDatabaseModal.show(); // ... то принудительно показываем модальное окно
        return false;
      }
      return true;
    },
  },
  components: {
    statusinfo: StatusInfo,
  },
  created() {
    this.dbType = getType(); // читаем из localStorage тип базы данных
    this.clearStatus(); // на всякий случай убираем статусный алерт
  },
  mounted() {
    if (this.checkDatabaseSelected()) { // если тип базы данных выбран (она есть в localStorage) ...
      this.getTodos(); // ... то обновляем список задач
    }
    // обрабатываем событие закрытие модальных окон
    this.$root.$on('bv::modal::hidden', (bvEvent, modalId) => {
      if (modalId === 'change-database-modal') { // если закрыто окно с выбором базы данных ...
        this.checkDatabaseSelected(); // ... то проверяем, выбрана ли база данных
      }
    });
  },
  computed: {
    dbCurrent() { // в зависимости от типа базы данных возвращяем ее текстовое представление
      if (this.dbType === null) return '';
      return this.dbType ? this.dbRemote : this.dbLocal;
    },
    todosCountDone() {
      return this.todos.filter((x) => (x.is_completed)).length;
    },
    todosCountNotDone() {
      return this.todos.filter((x) => (!x.is_completed)).length;
    },
  },
};
</script>

<style>
button#task-add {
  margin-top: 20px;
  margin-bottom: 20px;
}
h2, th, td {
  text-align: left;
}
.todo-uid {
  text-align: right;
}
</style>
