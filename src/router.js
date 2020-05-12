import Vue from 'vue';
import Router from 'vue-router';
import Todos from './components/Todos.vue';
// import Message from './components/Message.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    // {
    //   path: '/',
    //   name: 'message',
    //   component: Message,
    // },
    {
      // path: '/todos',
      path: '/',
      name: 'todos',
      component: Todos,
    },
  ],
});
