<template>
  <div>
    <p>{{ msg }}</p>
  </div>
</template>

<script>
import axios from 'axios';

const messageURL = 'http://localhost:5000/api/message';

export default {
  name: 'Message',
  data() {
    return {
      msg: 'Запрос ещё не прошёл',
    };
  },
  methods: {
    getMessage() {
      axios.get(messageURL)
        .then((response) => {
          this.msg = response.data.message;
        });
    },
  },
  created() {
    this.getMessage();
  },
};
</script>
