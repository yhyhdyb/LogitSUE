<script setup lang="ts">
import { useNetworksInfo } from "@/stores/networksInfo";
import { useNodes } from '@/stores/nodes';
import { useLinks } from '@/stores/links';
import {ref, computed, onMounted ,reactive } from 'vue'
const networksInfoData = useNetworksInfo()
const nodesData = useNodes()
const linksData = useLinks()

const state = reactive({
  items: [
    { text: '初始版本', isSelected: false, x: 50, y: 50  },
    // 添加更多的圆形数据...
  ],
});

const addSvg = (index: number) => {
  const newX = state.items[index].x + 50;
  const newY = state.items[index].y;
  state.items.splice(index + 1, 0, { text: '新的 SVG', isSelected: false , x: newX, y: newY});
};

networksInfoData.$subscribe((mutation, state) => {
  // 初始化列表西悉尼
  nodesData.nodesInitialization()
  linksData.linksInitialization()
})

function network_duplicate(network_idx:number) {
  // 复制路网
  console.log("network_idx:", network_idx);
  
  networksInfoData.networkDuplicate(network_idx)
}

function network_delete(network_idx:number, network_info: any) {
  // console.log(network_info);
  // return;
  if (network_idx<=0 || network_idx>=networksInfoData.networksInfoArr.length) {
    return
  }
  // 删除某个路网
  networksInfoData.networkDel(network_idx)
  // 删除路网相关信息
  nodesData.networkNodesDel(network_idx)
  linksData.networkLinksDel(network_idx)
}
const zoom_rat = ref(100)
const svg_box_width = ref(500)
const svg_box_height = ref(500)
const svg_x = ref(svg_box_width.value/2)
const svg_y = ref(svg_box_height.value/2)
const svg_width = ref(300)
const svg_height = ref(200)
// const mouse_push = ref(false)

// 计算属性
const svg_left = computed(() => {
  return svg_x.value-svg_width.value/2
})
const svg_top = computed(() => {
  return svg_y.value-svg_height.value/2
})

// 监听屏幕大小变化
function observeContainerSizeChanges(container: HTMLElement,
    callback: (width: number, height: number) => void) {
  const resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
      const { width, height } = entry.contentRect;
      callback(width, height);
    }
  });

  resizeObserver.observe(container);
}

function handle_mouse_move(event: MouseEvent) {
  if (event.buttons == 1) {
    // 鼠标左键被按下
    // 当右键被按下时为0
    // console.log(event);
    // 获取鼠标移动的偏移量
    const offsetX = event.movementX;
    const offsetY = event.movementY;

    // 处理鼠标移动的偏移量
    let svg_x_move = svg_x.value + offsetX
    let svg_zoom_rate = zoom_rat.value/100
    
    // 当svg内容是否超出盒子大小，处理方式相反
    if (svg_width.value*svg_zoom_rate < svg_box_width.value) {
      if (svg_x_move + svg_width.value/2*svg_zoom_rate > svg_box_width.value) {
        svg_x_move = svg_box_width.value - svg_width.value/2*svg_zoom_rate
      } else if (svg_x_move - svg_width.value*svg_zoom_rate/2 < 0) 
        svg_x_move = svg_width.value/2*svg_zoom_rate
    } else {
      if (svg_x_move + svg_width.value/2*svg_zoom_rate <= svg_box_width.value) {
        svg_x_move = svg_box_width.value - svg_width.value/2*svg_zoom_rate
      } else if (svg_x_move - svg_width.value*svg_zoom_rate/2 >= 0) 
        svg_x_move = svg_width.value/2*svg_zoom_rate
    }
    
    let svg_y_move = svg_y.value + offsetY
    if (svg_height.value*svg_zoom_rate < svg_box_height.value) {
      if (svg_y_move + svg_height.value/2*svg_zoom_rate > svg_box_height.value) {
        svg_y_move = svg_box_height.value - svg_height.value/2*svg_zoom_rate
      } else if (svg_y_move - svg_height.value*svg_zoom_rate/2 < 0) 
        svg_y_move = svg_height.value/2*svg_zoom_rate
    } else {
      if (svg_y_move + svg_height.value/2*svg_zoom_rate <= svg_box_height.value) {
        svg_y_move = svg_box_height.value - svg_height.value/2*svg_zoom_rate
      } else if (svg_y_move - svg_height.value*svg_zoom_rate/2 >= 0) 
        svg_y_move = svg_height.value/2*svg_zoom_rate
    }
    svg_x.value = svg_x_move
    svg_y.value = svg_y_move
    // svg_x.value += (offsetX)
    // svg_y.value += (offsetY)
    // console.log('X偏移量:', offsetX);
    // console.log('Y偏移量:', offsetY);
    // console.log(event);
    
  }
  // console.log(event);
}

function handle_wheel(event:WheelEvent) {
  console.log(event);
  const deltaX = event.deltaX;
  const deltaY = event.deltaY;
  if (deltaY > 0 && zoom_rat.value >= 20) {
    zoom_rat.value -= 10
  } else if (deltaY < 0) {
    zoom_rat.value += 10
  }
}

onMounted(() => {
  // 记录窗口大小
  const svg_box_target = document.getElementById("thumbnail_content_box") as HTMLDivElement
  observeContainerSizeChanges(svg_box_target, (width, height) => {
    svg_box_height.value = height
    svg_box_width.value = width
  })
})
</script>
<template>
  <div class="main_window">
    <div class="logo_box">
      <h1>
        Urban Countermeasure Simulation
      </h1>
    </div>
    <div class="thumbnail_box">
      <h2 class="box_title">
        Thumbnail
      </h2>
      <div id="thumbnail_content_box">
        <svg 
        :style="{ transform: `scale(${zoom_rat/100})`, left: svg_left, top: svg_top}"
        @mousemove="handle_mouse_move($event)"
        @wheel.stop="handle_wheel($event)">
          <circle 
            v-for="(item, index) in state.items" 
            :key="index"
            v-bind:class="{ 'selected': item.isSelected }" 
            :cx="item.x" 
            :cy="item.y" 
            r="20" 
            stroke="black" 
            stroke-width="3" 
            fill="blue" 
            @click="item.isSelected = !item.isSelected; addSvg(index)"
          />
          <text v-for="(item, index) in state.items" 
          :key="index"
          :x="item.x" :y="item.y" text-anchor="middle" fill="white">{{ item.text }}</text>
        </svg>
      </div>
      <div class="zhanwei" style="width: 100%; height: 20px;"></div>
    </div>
    <div class="map_layers_box">
      <h2 class="box_title">
        Network Layers
      </h2>
      <div class="map_layers_content_box">
        <div class="map_layer_block" v-for="(network_info, idx) in networksInfoData.networksInfoArr" :key="idx">
          <div class="layer_btn_box">
            <input type="checkbox" name="" id="" class="layer_show_select" v-model="networksInfoData.networkShow[idx]">
            <button class="layer_show_btn" @click="network_duplicate(idx)">
              <img src="/static/duplicate.png" alt="" srcset="">
            </button>
            <button class="layer_show_btn" v-if="network_info.id>0" @click="network_delete(idx, network_info)">
              <img src="/static/trash.png" alt="" srcset="">
            </button>
          </div>
          <img src="https://ts1.cn.mm.bing.net/th/id/R-C.53f002e233cbdf84aa4cd50e940eb061?rik=hofYjzuvBbUjOA&riu=http%3a%2f%2fwww.civilcn.com%2fd%2ffile%2fjianzhu%2fjztz%2fguihua%2f2016-05-25%2ffc00d4df6b7cab9612d8ef3392b5cd63.png&ehk=vhtnkWlpkKH%2fJytlsXMtifEkp9bwsS0uuCdTN4K%2bF8I%3d&risl=&pid=ImgRaw&r=0"
            alt="" height="80px" width="60px" srcset="">
          <div class="map_layer_info">
            <div class="map_layer_title">
              <input type="text" class="map_layer_title_ipt" v-model="network_info.title"
              placeholder="Layer Title">
            </div>
            <div class="map_layer_desc">
              <textarea name="" id="" cols="30" rows="3" v-model="network_info.desc"
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
.thumbnail_box,
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
.thumbnail_content_box {
  margin-left: 20px;
  margin-right: 20px;
  border: 1px solid #aaa;
  /* width: calc(100% - 40px); */
  width: 260px;
  height: 300px;
  /* background-color: aqua; */
}

/* 图层框 */
.map_layers_box {
  /* min-height: calc(100% - 443px); */
  height: calc(100% - 443px);
  /* overflow: scroll; */
  padding-bottom: 0;
}

.map_layers_content_box {
  width: 260px;
  padding: 10px;
  height: calc(100% - 50px);
  padding-top: 0;
  padding-bottom: 0;
  overflow-y: scroll;
  overflow-x: hidden;
}

/* 单个图层的内容 */
.map_layer_block {
  display: flex;
  flex-direction: row;
  justify-items: center;
  align-items: center;
  text-align: center;
  border-radius: 5px;

  width: 100%;
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
