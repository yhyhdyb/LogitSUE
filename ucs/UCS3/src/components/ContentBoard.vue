<script setup lang="ts">
import TreeBoard from './TreeBoard.vue';
import MapBoard from './MapBoard.vue';

</script>
<template>
  <div class="main_board">
    <div class="map_board">
      <MapBoard></MapBoard>
    </div>
    <div class="tree_board">
      <TreeBoard></TreeBoard>
    </div>
  </div>
</template>

<style scoped>
.main_board {
  width: 100%;
  height: 100%;

  display: flex;
  flex-direction: row;
  align-items: center;
}
.map_board {
  height: 100%;
  width: 60%;
  margin-right: 4px;
}
.tree_board {
  height: 100%;
  width: calc(40% - 4px);
}

</style>