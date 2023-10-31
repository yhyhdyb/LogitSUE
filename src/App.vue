<template>
  <div id="app">
    <indexView />
  </div>
</template>
<script lang="ts">
import indexView from "./components/index.vue";

export default {
  name: "App",
  components: {
    indexView,
  },

  setup() {
    return {};
  },
};
</script>
<style lang="scss">
html,
body,
#app {
  width: 100%;
  height: 100%;
  margin: 0;
}
</style>
