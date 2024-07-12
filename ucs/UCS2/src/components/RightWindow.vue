<script setup lang="ts">
import InfoBox from './InfoBox.vue';
// import { useNetworksData } from '@/stores/networkData';
import { useLineEdit } from '@/stores/lineEdit';
import WorkTree from "./WorkTree.vue";
import littleMapBox from './littleMapBox.vue';
const lineEditData = useLineEdit()

function handle_new_line() {
  // lineEditData.editState = 
  lineEditData.startDraw()
}

</script>
<template>
  <div class="main_window">
    <div class="control_box">
      <h2 class="box_title">
        Control Panel
      </h2>
      <div class="control_btns_box">
        <span class="control_btn" @click="handle_new_line">
            <img src="/static/highlighter-line.png" alt="" srcset="">
        </span>
      </div>
      <div class="zhanwei" style="width: 100%; height: 10px;"></div>
    </div>
    <div class="network_info_box">
      <InfoBox/>
    </div>
    <div class="tree_box">
      <h2 class="box_title">
        Workflow
      </h2>
      <div class="tree_content_box">
        <WorkTree />
      </div>
      <div class="zhanwei" style="width: 100%; height: 20px;"></div>
    </div>
    <div class="container_box">
      <littleMapBox/>
    </div>
  </div>
</template>

<style scoped>

.main_window {
  width: 100%;
  height: 100%;
  overflow: auto;
}
.tree_content_box {
  margin-left: 20px;
  margin-right: 20px;
  border: 1px solid #aaa;
  /* width: calc(100% - 40px); */
  width: 100%;
  height: 200px;
  /* background-color: aqua; */
}
/* 缩略图 */
.control_box,
.network_info_box {
  text-align: center;

  /* margin-top: 5px; */
  width: 100%;
  /* height: 450px; */
  background-color: #F6F6F6;
  box-shadow: 0px 5px 5px rgba(0,0,0,0.2);
  border-radius: 5px;
}

.control_btns_box {
  margin: 10px;
  width: calc(100% - 20px);
  text-align: center;
  display: block;
  position: relative;
  margin-top: 0;
  margin-bottom: 0;
}
.control_btns_box .control_btn {
    background-color: #dadada;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    margin: 10px;
    display: inline-block;
    margin-top: 5px;
    margin-bottom: 5px;

    /* position: relative;
    display: flex;
    justify-items: center;
    align-items: center;
    text-align: center; */
}

.control_btns_box .control_btn:hover {
  filter: brightness(1.2);
  cursor: pointer;
}

.control_btns_box .control_btn img {
    width: 20px;
    height: 20px;
    margin-top: 5px;
    margin-bottom: auto;
    margin-left: auto;
    margin-right: auto;
    justify-items: center;
    align-items: center;
}

/* 图层框 */
.network_info_box {
  margin-top: 5px;
  height: calc(50% - 30px);
}

.container_box {
  margin-top: 5px;
  height: 100%;
}
/* 各部分小标题 */
.main_window .box_title {
  font-size: 16px;
  font-weight: 350;
  color: #808080;
  text-align: left;

  padding: 10px;
  padding-left: 20px;
  padding-right: 20px;
  margin: 0;
}
</style>
