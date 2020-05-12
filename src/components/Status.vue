<template>
  <div @dblclick="stopAutoDimiss">
    <b-alert
      :variant="variant"
      dismissible
      @dismissed="clearStatus"
      :show="showIt">
      {{ message }}
    </b-alert>
  </div>
</template>

<script>
export default {
  props: ['message', 'variant', 'showIt'],
  methods: {
    clearStatus() { // вызываем родительское событие clear, когда вышло время у b-alert
      this.$emit('clear');
    },
    stopAutoDimiss() { // вызываем родительское событие stop по двойному клику на поле статуса
      this.$emit('stop');
    },
  },
};
</script>
