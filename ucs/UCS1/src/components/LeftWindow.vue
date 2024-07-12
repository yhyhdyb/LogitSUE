<script setup lang="ts">
import WorkTree from "./WorkTree.vue";



</script>
<template>
  <div class="main_window">
    <div class="logo_box">
      <h1>
        Urban Countermeasure Simulation
      </h1>
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
    <div class="map_layers_box">
      <h2 class="box_title">
        Network Layers
      </h2>
      <div class="map_layers_content_box">
        <div class="map_layer_block">
          <div class="layer_btn_box">
            <input type="checkbox" name="" id="" class="layer_show_select">
            <button class="layer_show_btn">
              <img src="/static/duplicate.png" alt="" srcset="">
            </button>
            <button class="layer_show_btn">
              <img src="/static/trash.png" alt="" srcset="">
            </button>
          </div>
          <img src="https://ts1.cn.mm.bing.net/th/id/R-C.53f002e233cbdf84aa4cd50e940eb061?rik=hofYjzuvBbUjOA&riu=http%3a%2f%2fwww.civilcn.com%2fd%2ffile%2fjianzhu%2fjztz%2fguihua%2f2016-05-25%2ffc00d4df6b7cab9612d8ef3392b5cd63.png&ehk=vhtnkWlpkKH%2fJytlsXMtifEkp9bwsS0uuCdTN4K%2bF8I%3d&risl=&pid=ImgRaw&r=0"
            alt="" height="80px" width="60px" srcset="">
          <div class="map_layer_info">
            <div class="map_layer_title">
              <input type="text" class="map_layer_title_ipt"
              placeholder="Layer Title">
            </div>
            <div class="map_layer_desc">
              <textarea name="" id="" cols="30" rows="3"
              class="map_layer_desc_ipt" placeholder="Layer Description"></textarea>
              <!-- <input type="text" class="map_layer_title_ipt"> -->
            </div>
          </div>
        </div>
        
      </div>
      <!-- <div class="zhanwei" style="width: 100%; height: 20px;"></div> -->
    </div>
  </div>
</template>

<style scoped>
.main_window {
  width: 100%;
  height: 100%;
  z-index: 2;
  position: relative;
  /* overflow: auto; */
}

/* logo框 */
.logo_box {
  width: 100%;
  background-color: #F6F6F6;
  border-radius: 5px;
  box-shadow: 0px 5px 5px rgba(0,0,0,0.2);
}

/* 总标题 */
.logo_box h1 {
  font-size: 20px;
  font-weight: 300;

  padding: 8px;
  text-align: center;
  margin: 0;
}

/* 缩略图 */
.tree_box,
.map_layers_box {
  text-align: center;

  margin-top: 5px;
  width: 100%;
  /* height: 450px; */
  background-color: #F6F6F6;
  box-shadow: 0px 5px 5px rgba(0,0,0,0.2);
  border-radius: 5px;
}

/* 缩略图内容盒子 */
.tree_content_box {
  margin-left: 20px;
  margin-right: 20px;
  border: 1px solid #aaa;
  /* width: calc(100% - 40px); */
  width: 260px;
  height: 200px;
  /* background-color: aqua; */
}

/* 图层框 */
.map_layers_box {
  /* min-height: calc(100% - 443px); */
  /* height: calc(100% - 443px); */
  height: calc(100% - 343px);
  /* overflow: scroll; */
  padding-bottom: 0;
  text-align: center;
}

.map_layers_content_box {
  width: 260px;
  padding: 10px;
  height: calc(100% - 50px);
  padding-top: 0;
  padding-bottom: 0;
  text-align: center;
  /* overflow-y: scroll; */
  overflow-y: auto;
  overflow-x: hidden;

  margin-left: auto;
  margin-right: auto;
}

/* 单个图层的内容 */
.map_layer_block {
  display: flex;
  flex-direction: row;
  justify-items: center;
  align-items: center;
  text-align: center;
  border-radius: 5px;

  width: calc(100% - 20px);
  height: 80px;
  padding: 10px;
  margin: 10px;
  margin-top: 0;
  margin-left: auto;
  margin-right: auto;
  background-color: #fafafa;
  box-shadow: 2px 2px 2px rgba(0,0,0,0.2);
}

/* 各个图层的按钮 */
.map_layer_block .layer_btn_box {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.map_layer_block .layer_show_btn {
  width: 20px;
  height: 20px;
  text-decoration: none;
  background-color: #ffffffaa;
  margin: 5px;
  border: 0;
  padding: 1px;
  border-radius: 20%;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  cursor: pointer;
}
.map_layer_block .layer_show_btn img {
  /* margin-left: 10px; */
  width: 10px;
  height: 10px;
  margin-left: auto;
  margin-right: auto;
}

.map_layer_block .layer_show_btn:hover {
  filter: brightness(0.8);
}

.map_layer_block img, .map_layer_block svg {
  margin: 10px;
  margin-left: 0;
}

.map_layer_block .layer_show_select {
  margin: 5px;
  cursor: pointer;
}


.map_layer_info {
  height: 100%;
  width: 150px;
}

/* 每张layer的标题 */
.map_layer_info .map_layer_title {
  width: 100%;
  margin-bottom: 5px;
}
.map_layer_info .map_layer_title_ipt {
  text-decoration: none;
  width: 100%;
  border: 1px solid #F6F6F6;
  background-color: #F6F6F600;
  outline: none;
}
.map_layer_desc .map_layer_title_ipt:focus {
  outline: none;
  box-shadow: 1px 1px 1px rgba(255,255,255,0.2);
}

/* 每张layer的描述 */
.map_layer_desc .map_layer_desc {
  width: 100%;
}
.map_layer_desc .map_layer_desc_ipt {
  text-decoration: none;
  width: 100%;
  border: 1px solid #F6F6F6;
  resize: none;
  background-color: #F6F6F600;
}
.map_layer_desc .map_layer_desc_ipt:focus {
  outline: none;
  box-shadow: 1px 1px 1px rgba(255,255,255,0.2);
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