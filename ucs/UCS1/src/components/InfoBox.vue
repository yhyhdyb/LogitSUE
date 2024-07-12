<script setup lang="ts">
import { useLineEdit } from '@/stores/lineEdit';
import { useNetworksData } from '@/stores/networkData';
import { computed, watch } from 'vue';

const lineEditData = useLineEdit()
const networkData = useNetworksData()

// 监听终点是否发生变化
watch(
  () => lineEditData.endNodeIdx,
  () => {
    if (lineEditData.editState == 1) {
      const start_idx = lineEditData.startNodeIdx
      const end_idx = lineEditData.endNodeIdx
      const network_idx = lineEditData.networkIdx
      if (start_idx != -1 && end_idx != -1 && network_idx != -1) {
        const start_node = networkData.networksInfoArr[network_idx].nodes[start_idx]
        const end_node = networkData.networksInfoArr[network_idx].nodes[end_idx]
        const link_len = Math.sqrt((start_node.lat-end_node.lat)*
          (start_node.lat-end_node.lat)+(start_node.lon-end_node.lon)*(start_node.lon-end_node.lon))
        // 重新计算free flow travel time
        lineEditData.newFreeFlowTravelTime = Math.ceil(link_len*240)
        lineEditData.newIFreeFlowTravelTime = Math.ceil(link_len*240)
      }
    }
  }
)

function node_pos2str(node_idx: number, network_idx: number) {
  // 将节点经纬度转化为字符串
  let res = ""
  if (node_idx != -1 && network_idx != -1) {
    const start_node = networkData.networksInfoArr[network_idx].nodes[node_idx]
    const lat = start_node.lat
    const lng = start_node.lon
    if (lat>0) res += lat.toFixed(5) + "°N, "
    else res += (-lat).toFixed(5) + "°S, "
    if (lng>0) res += lng.toFixed(5) + "°E"
    else res += (-lng).toFixed(5) + "°W"
    return res
  } else return "None"
}

const start_pos = computed(() => {
  const start_node_idx = lineEditData.startNodeIdx
  const edit_network_idx = lineEditData.networkIdx
  return node_pos2str(start_node_idx, edit_network_idx)
})

const end_pos = computed(() => {
  const end_node_idx = lineEditData.endNodeIdx
  const edit_network_idx = lineEditData.networkIdx
  return node_pos2str(end_node_idx, edit_network_idx)
})

const backward_btn_text = computed(() => {
  if (lineEditData.isBidirection) return "︿ One-Way Road"
  return "﹀ Two-Way Road"
})

// 切换单双行道
function way_on_road() {
  lineEditData.isBidirection = !lineEditData.isBidirection
}

// 取消划线
function cancel_draw_new() {
  lineEditData.editState = 0
}

// 保存新建的道路
async function save_new_road() {
  if (lineEditData.editState != 1) {
    console.log("New Link Error: 当前为不可修改的状态");
    return
  }
  let networkIdx = lineEditData.networkIdx
  networkIdx =  await networkData.networkDuplicate(networkIdx)
  

  const startPtId = lineEditData.startNodeIdx
  const endPtId = lineEditData.endNodeIdx
  // return
  const capacity = lineEditData.newCapacity
  const freeFlowTravelTime = lineEditData.newFreeFlowTravelTime
  const iCapacity = lineEditData.newICapacity
  const iFreeFlowTravelTime = lineEditData.newIFreeFlowTravelTime
  const iExist = lineEditData.isBidirection
  await networkData.newLink(networkIdx, startPtId, endPtId, 
    freeFlowTravelTime, capacity, iFreeFlowTravelTime, iCapacity, iExist)
  lineEditData.endDraw()
}

// 保存对路段的修改
async function save_link_change() {
  if (lineEditData.editState != 2) {
    console.log("New Link Error: 当前为不可修改的状态");
    return
  }
  let networkIdx = lineEditData.networkIdx
  networkIdx =  await networkData.networkDuplicate(networkIdx)

  // 开始保存修改
  const new_capacity = lineEditData.newCapacity
  const new_free_flow_travel_time = lineEditData.newFreeFlowTravelTime
  const link_idx_to_change = lineEditData.lineIdx
  await networkData.resetLink(networkIdx, link_idx_to_change, new_free_flow_travel_time, new_capacity)
  lineEditData.endDraw()
}
</script>
<template>
  <div class="content_box">
    <h2 class="box_title">
      Road Network Info
    </h2>
    <div class="info_block">
      <h3 class="block_title">
        Endpoints
      </h3>
      <div class="attr_pair">
        <div class="attr_title">
          Starting Postion
        </div>
        <div class="attr_val">
          {{ start_pos }}
        </div>
      </div>
      <div class="attr_pair">
        <div class="attr_title">
          Ending Postion
        </div>
        <div class="attr_val">
          {{ end_pos }}
        </div>
      </div>
    </div>
    <div class="info_block">
      <h3 class="block_title">
        Forward Link Info
      </h3>
      <div class="attr_pair">
        <div class="attr_title">
          Capacity
        </div>
        <div class="attr_val">
          <input type="number" class="attr_ipt" v-model="lineEditData.newCapacity">
        </div>
      </div>
      <div class="attr_pair">
        <div class="attr_title">
          Free Flow Travel Time
        </div>
        <div class="attr_val">
          <input type="number" class="attr_ipt" v-model="lineEditData.newFreeFlowTravelTime">
        </div>
      </div>
      <div id="thumbnail" style="width: 100%; height: 100%;"></div>
    </div>
    
    <div class="info_block" v-show="lineEditData.isBidirection">
      <h3 class="block_title">
        Backward Link Info
      </h3>
      <div class="attr_pair">
        <div class="attr_title">
          Capacity
        </div>
        <div class="attr_val">
          <input type="number" class="attr_ipt" v-model="lineEditData.newICapacity">
        </div>
      </div>
      <div class="attr_pair">
        <div class="attr_title">
          Free Flow Travel Time
        </div>
        <div class="attr_val">
          <input type="number" class="attr_ipt" v-model="lineEditData.newIFreeFlowTravelTime">
        </div>
      </div>
    </div>
    <div class="info_block" v-show="lineEditData.editState==1">
      <div class="backward_set_btn" @click="way_on_road()">
        {{ backward_btn_text }}
      </div>
    </div>
    <div class="info_block btn_box" v-show="lineEditData.editState==1">
      <button class="info_block_btn" @click="save_new_road()">New</button>
      <button class="info_block_btn" @click="cancel_draw_new()">Cancel</button>
    </div>
    <div class="info_block btn_box" v-show="lineEditData.editState==2">
      <button class="info_block_btn" @click="save_link_change()">Save</button>
      <button class="info_block_btn">Cancel</button>
    </div>
    <div class="zhanwei" style="width: 100%; height: 20px;"></div>
  </div>
</template>
<style scoped>
.content_box {
  width: 100%;
  height: 100%;
}

.content_box .info_block {
  margin: 10px 20px;

  transition: all 0.2s ease;
}

.content_box .info_block .block_title {
  text-align: left;
  font-size: 14px;
  font-weight: 400;

  color: #8a8a8a;
  margin: 10px;
  margin-bottom: 0;
}

.content_box .info_block .attr_pair {
  padding: 5px;
  text-align: left;
}

.content_box .info_block .attr_pair .attr_title {
  font-size: #5a5a5a;
  font-size: 14px;
}
.content_box .info_block .attr_pair .attr_val {
  font-size: #000;
  font-size: 16px;
}

/* 输入框 */
.attr_val .attr_ipt {
  margin-top: 2px;
  padding: 2px 5px;
  width: calc(100% - 12px);
  font-size: 16px;
  background-color: #ffffffaa;
  border: 1px solid #aaa;
  border-radius: 3px;
  outline: none;
}
.attr_val .attr_ipt:focus {
  border-color: #808080;
}

.box_title {
  font-size: 16px;
  font-weight: 350;
  color: #808080;
  text-align: left;

  padding: 10px;
  padding-left: 20px;
  padding-right: 20px;
  margin: 0;
}

/* 按钮 */
.btn_box {
  text-align: center;
}
.info_block .info_block_btn {
  width: calc(50% - 10px);
  padding: 5px 10px;
  margin: 5px;

  cursor: pointer;
}

/* 单双向道路控制 */
.info_block .backward_set_btn {
  width: 100%;
  text-align: center;
  font-size: 12px;
  color: #aaa;
  user-select: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.info_block .backward_set_btn:hover {
  filter: brightness(0.8);
}
</style>
