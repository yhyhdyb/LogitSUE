<script setup lang="ts">
import HistorgramGraph from './HistorgramGraph.vue'
import SortSelBoard from './SortSelBoard.vue'

//
const hist_graphs_id = [0, 1, 2, 3, 4, 5, 6, 7]
</script>
<template>
  <div class="filter_main_board">
    <div class="historgrams_info_block">
      <div class="historgram_block" v-for="graph_ctn_id in hist_graphs_id" :key="graph_ctn_id">
        <HistorgramGraph :content_id="graph_ctn_id"></HistorgramGraph>
      </div>
    </div>
    <div class="sort_conds_block">
      <SortSelBoard></SortSelBoard>
    </div>
  </div>
</template>

<style scoped>
.filter_main_board {
  width: 100%;
  height: 100%;
  /* border-radius: 8px; */
  background-color: grey;
  /* box-shadow: 2px 5px 5px rgba(255,255,255,0.2); */

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-items: center;
  text-align: center;
}

.main_board .historgrams_info_block {
  margin-left: auto;
  margin-right: auto;
  width: calc(100% - 14px);
  /* height: calc(100% - 18px - 45px); */
  height: 112px;
  border-radius: 3px;
  padding: 7px;
  padding-top: 9px;
  padding-bottom: 5px;

  /* background-color: aliceblue; */
  overflow: hidden;

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-items: center;
  text-align: center;
}

.historgrams_info_block .historgram_block {
  width: 120px;
  height: 112px;
  /* width: 100%; */
  margin: auto;
  /* padding: 2px; */
  border-radius: 3px;

  /* display: flex;
  flex-direction: row;
  align-items: center;
  justify-items: center;
  text-align: center; */
}

.sort_conds_block {
  width: calc(100% - 18px);
  height: 40px;
  display: block;
}
</style>
