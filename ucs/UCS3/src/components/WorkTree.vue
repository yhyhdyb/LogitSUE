<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useNetworksData } from '@/stores/networkData';
import { useNetworkSel } from '@/stores/networkSel';

// const networksInfoData = useNetworksInfo()
const networkData = useNetworksData()
const networkSel = useNetworkSel()

// 树样式相关的值
const circle_radius = 25
const horizontal_dis = 80
const vertical_dis = 50
const horizontal_padding = 50
const vertical_padding = 50
const node_block_half_width = 80
const node_block_half_height = 60
const node_block_radius = 5

// 删除的工具栏
const menuBottom = ref(-30)

// 树结构相关的值
const work_states = ref([
  {level_idx: 0, idx_in_level: 0, fill_color: {r: 100, g: 255, b: 100}}
])
const tree_fathers_idx = ref([-1])
const tree_childs_idxs = ref([[]] as number[][])

// 可以被重新赋值的元素
const tree_width = ref(1)
const tree_depth = ref(1)
const tree_structure = ref([[0]] as number[][])
const node_showing = ref([false])
const now_showing_one = ref(-1)

// svg的长宽
const svg_width = computed(()=> {
  return 2*node_block_half_width*(tree_depth.value) + 
    horizontal_dis*(tree_depth.value-1) + 
    2*horizontal_padding
})

const svg_height = computed(()=> {
  return 2*node_block_half_height*(tree_width.value) + 
    vertical_dis*(tree_width.value-1) + 
    2*vertical_padding
})

// 每个点在svg中位置
const nodes_pos = computed(() => {
  const nodes_position = [] as {x:number,y:number, fill_color:string}[]
  for (let i=0; i<work_states.value.length; i++) {
    let level_idx = work_states.value[i].level_idx
    let idx_in_level = work_states.value[i].idx_in_level
    let row_num = tree_structure.value[level_idx].length

    // 矩形的设置方法
    let node_x = horizontal_padding + level_idx*(2*node_block_half_width+horizontal_dis)
    let node_y = svg_height.value/2 + 
      (idx_in_level-(row_num-1)/2)*(2*node_block_half_height+vertical_dis) -
      node_block_half_height

    // 圆形的设置方法
    // let node_x = horizontal_padding + level_idx*(2*circle_radius+horizontal_dis)+circle_radius
    // let node_y = svg_height.value/2+(idx_in_level-(row_num-1)/2)*(2*circle_radius+vertical_dis)

    let node_fill = 'rgba(' + work_states.value[i].fill_color.r + ',' 
      + work_states.value[i].fill_color.g + ',' + work_states.value[i].fill_color.b + ',0.5)'
    nodes_position.push({x:node_x, y:node_y, fill_color: node_fill})
  }
  return nodes_position
})

// 每个线段在svg中位置
const node_lines_pos = computed(() => {
  const lines_pos = [] as string[]
  let now_nodes_pos = nodes_pos.value
  for (let i=0; i<tree_childs_idxs.value.length; i++) {
    for (let j=0; j<tree_childs_idxs.value[i].length; j++) {
      let start_node = now_nodes_pos[i]
      let end_node = now_nodes_pos[tree_childs_idxs.value[i][j]]
      // M 10 10 C 50 10, 10 50, 50 50
      // 圆形设置方法
      // let start_x = start_node.x + circle_radius
      // let start_y = start_node.y
      // let end_x = end_node.x - circle_radius
      // let end_y = end_node.y

      // 矩形的设置方法
      let start_x = start_node.x+2*node_block_half_width
      let start_y = start_node.y+node_block_half_height
      let end_x = end_node.x
      let end_y = end_node.y+node_block_half_height

      let path_d = "M" + start_x + " " + start_y + " C " + 
        end_x + " " + start_y + ", " + start_x + " " + 
        end_y + ", " + end_x + " " + end_y
      lines_pos.push(path_d)
    }
  }
  return lines_pos
})

// 每个点的样式
function node_block_classlist(node_idx:number) {
  const is_sel = networkSel.networks_show.indexOf(node_idx)!=-1
  const is_last_sel = networkSel.last_sel_network_id==node_idx
  const node_class_list = {
    to_be_del: del_sel_node_idx.value==node_idx,
    now_show: is_sel && !is_last_sel, 
    last_showing_one: is_sel && is_last_sel
  }
  return node_class_list
}

// 获取节点颜色
function get_node_color(origin_color:{r:number, g:number, b:number}, level_num:number) {
  // 获取变化颜色范围
  if (level_num > 6) level_num = 5
  let abs_color_scope = 60/(2**level_num)
  abs_color_scope = Math.random()*(abs_color_scope/4)+abs_color_scope/2
  let color_scope = abs_color_scope+120
  // if (Math.random()-0.5<0) color_scope = 120-abs_color_scope
  // else color_scope += 120
  

  // 原始颜色类型取整
  let origin_scope = 255*3-100*3-(origin_color.r+origin_color.g+origin_color.b)
  origin_scope = origin_scope-Math.floor(origin_scope/155)*(155)
  color_scope -= (origin_scope/155*20)
  let color_type_mv = Math.floor(color_scope/20)
  
  let former_color_type = 0
  // 判断原始颜色类型
  if (origin_color.b==255 && origin_color.r==100 && origin_color.g < 255) {
    former_color_type = 1
  } else if (origin_color.b==255 && origin_color.r>100 && origin_color.g==100) {
    former_color_type = 2
  } else if (origin_color.b<255 && origin_color.r==255 && origin_color.g==100) {
    former_color_type = 3
  } else if (origin_color.r==255 && origin_color.g>100 && origin_color.b==100) {
    former_color_type = 4
  } else if (origin_color.r<255 && origin_color.g==255 && origin_color.b==100) {
    former_color_type = 5
  }

  let res_color_type = Math.floor(former_color_type+color_type_mv)
  res_color_type = res_color_type-Math.floor(res_color_type/6)*6
  let in_color_scope = (color_scope-color_type_mv*20)/20*155
  
  // 获取最终颜色
  let res_color = {r: 100, g:255-in_color_scope, b:255}
  if (res_color_type == 1) {
    res_color = {r: 100+in_color_scope, g:100, b:255}
  } else if (res_color_type == 2) {
    res_color = {r: 255, g:100, b:255-in_color_scope}
  } else if (res_color_type == 3) {
    res_color = {r: 255, g:100+in_color_scope, b:100}
  } else if (res_color_type == 4) {
    res_color = {r: 255-in_color_scope, g:255, b:100}
  } else if (res_color_type == 5) {
    res_color = {r: 100, g:255, b:100+in_color_scope}
  }
  
  return res_color
}

// 重新计算树中各个节点的位置等属性
function set_nodes_pos() {
  let nodes_que = [0]
  let nxt_level_que = [] as number[]
  let now_pos = 0
  let now_level = 0
  let now_idx_in_level = 0
  tree_width.value = 1
  tree_structure.value = [[]]
  while(now_pos < nodes_que.length) {
    let now_node_idx = nodes_que[now_pos]
    if (now_node_idx >= 0) {
      // 将该节点的子节点加入下一层的数组
      for (let i=0; i<tree_childs_idxs.value[now_node_idx].length; i++) {
        nxt_level_que.push(tree_childs_idxs.value[now_node_idx][i])
      }

      // 设置该节点信息
      work_states.value[now_node_idx].level_idx = now_level
      work_states.value[now_node_idx].idx_in_level = now_idx_in_level
      now_idx_in_level += 1
      tree_structure.value[now_level].push(now_node_idx)
    }

    now_pos += 1
    if (now_pos == nodes_que.length) {
      // 更新树的宽度
      if (now_idx_in_level > tree_width.value) {
        tree_width.value = now_idx_in_level
      }

      now_pos = 0
      nodes_que = nxt_level_que
      nxt_level_que = []
      now_level += 1
      now_idx_in_level = 0
      tree_structure.value.push([])
    }
  }
  tree_depth.value = now_level
}

// 添加一个节点
function add_layer(father_id: number) {
  let id = work_states.value.length
  const now_color = get_node_color(work_states.value[father_id].fill_color, work_states.value[father_id].level_idx+1)
  work_states.value.push({
    level_idx: -1,
    idx_in_level: -1,
    fill_color: now_color
  })
  // 添加父节点关系
  tree_fathers_idx.value.push(father_id)
  tree_childs_idxs.value[father_id].push(id)

  // 添加子节点位置
  tree_childs_idxs.value.push([])
  set_nodes_pos()
}

// 删除一个节点
function del_layer(node_id:number) {
  if (menuBottom.value != 0 || node_id <= 0) return
  let father_id = tree_fathers_idx.value[node_id]

  // 删去其父节点的子节点
  tree_childs_idxs.value[father_id] = 
    tree_childs_idxs.value[father_id].filter(item => item != node_id)
  // 改变子节点的父节点
  for (let i=0; i<tree_childs_idxs.value[node_id].length; i++) {
    let child_id = tree_childs_idxs.value[node_id][i]
    tree_fathers_idx.value[child_id] = father_id
  }

  // 在workstate中删除该元素
  work_states.value.splice(node_id, 1)

  // 删除其父子节点数组
  tree_fathers_idx.value.splice(node_id, 1)
  tree_childs_idxs.value.splice(node_id, 1)

  // 重新移动下标
  for (let i=0; i<tree_fathers_idx.value.length; i++) {
    if (tree_fathers_idx.value[i] > node_id) {
      tree_fathers_idx.value[i] -= 1
    }
  }
  for (let i=0; i<tree_childs_idxs.value.length; i++) {
    for (let j=0; j<tree_childs_idxs.value[i].length; j++) {
      if (tree_childs_idxs.value[i][j] > node_id) {
        tree_childs_idxs.value[i][j] -= 1
      }
    }
  }

  // 重新赋值树的结构
  set_nodes_pos()
}

function recursion_del_layers(node_id:number) {
  if (menuBottom.value != 0 || node_id <= 0) return []
  const nodes_to_del = [node_id]
  let now_pos = 0
  console.log(tree_childs_idxs.value);
  
  while (now_pos < nodes_to_del.length) {
    let now_node_id = nodes_to_del[now_pos]
    console.log("now_node_id: ", now_node_id);
    
    for (let i=0; i<tree_childs_idxs.value[now_node_id].length; i++) {
      nodes_to_del.push(tree_childs_idxs.value[now_node_id][i])
    }
    now_pos += 1
  }
  nodes_to_del.sort((a,b) => a-b)
  for (let i=nodes_to_del.length-1; i>=0; i--) {
    del_layer(nodes_to_del[i])
  }
  return nodes_to_del
}

// 与仓库链接

watch(
  () => networkData.networksFatherIdx,
  (newValue: number[], oldValue: number[]) => {
    work_states.value.splice(1, work_states.value.length-1)
    tree_fathers_idx.value = [-1]
    tree_childs_idxs.value = [[]]
    for (let i=1; i<newValue.length; i++) {
      add_layer(newValue[i])
    }
  },
  {deep: true}
)

// 滚轮事件
const zoomRat = ref(100)
const svgLeft = ref(0)
const svgTop = ref(0)

// 滚轮放大缩小
function handleWheel(e:WheelEvent) {
  // console.log(e);
  if (e.deltaY > 0 && zoomRat.value > 20) {
    zoomRat.value /= 1.2
  } else if (e.deltaY < 0) {
    zoomRat.value *= 1.2
  }
}

// 移动事件
function handleMouseMove(e:MouseEvent) {
  // console.log(e);
  // 当左键被按下
  if (e.buttons == 1) {
    // console.log(e);
    let d_x = e.movementX
    let d_y = e.movementY
    svgLeft.value += d_x
    svgTop.value += d_y
  }
}

const del_sel_node_idx = ref(-1)

// 删除键的设置
function handleMenuDel() {
  let node_to_del = del_sel_node_idx.value
  
  // 在本文件逻辑中删除
  del_layer(node_to_del)
  // 在store中删除
  networkData.networkDelete(node_to_del)
  networkSel.deleteNetwork(node_to_del)

  del_sel_node_idx.value = -1
  menuBottom.value = -30
}
function handleMenuRecursionDel() {
  let node_to_del = del_sel_node_idx.value

  // 在本文件逻辑中删除
  const nodes_del = recursion_del_layers(node_to_del)
  // 在store中删除
  networkSel.deleteNetworks(nodes_del)
  networkData.networkRecursionDelete(nodes_del)

  del_sel_node_idx.value = -1
  menuBottom.value = -30
}

// 右键事件
function handleMenu(e: MouseEvent) {
  // console.log(e);
  e.preventDefault();
  const circle_element = e.target as HTMLElement
  let layer_id = parseInt(circle_element.getAttribute("circle_id") as string)
  
  if ((menuBottom.value == 0 && del_sel_node_idx.value == layer_id) ||
    layer_id == 0) {
    del_sel_node_idx.value = -1
    menuBottom.value = -30
    return
  }
  del_sel_node_idx.value = layer_id
  menuBottom.value = 0
}

function handleNetworkShow(e:MouseEvent) {
  // 左键单机nodeblock事件
  const circle_element = e.target as HTMLElement
  let layer_id = parseInt(circle_element.getAttribute("circle_id") as string)
  networkSel.selectNetwork(layer_id)
  // console.log("clicked ");
  
  return
}

// 自启动项
onMounted(() => {
  // add_layer(0)
  // add_layer(0)
})
</script>
<template>
  <div class="main_window">
    <svg version="1.1" class="tree_svg"
      baseProfile="full"
      :width="svg_width" :height="svg_height"
      xmlns="http://www.w3.org/2000/svg"
      @wheel="handleWheel" @mousemove="handleMouseMove"
      :style="{transform: `scale(${zoomRat/100})`, left: svgLeft, top: svgTop}">
      <path class="layers_link" v-for="(path_d, path_idx) in node_lines_pos" :key="path_idx"
       :d="path_d"/>
      <rect v-for="(node_pos, node_idx) in nodes_pos" :key="node_idx" :circle_id="node_idx"
        :x="node_pos.x" :y="node_pos.y" :width="node_block_half_width*2" :height="node_block_half_height*2"
        :rx="node_block_radius" :ry="node_block_radius" fill="#409eff"
        @contextmenu="handleMenu" @click="handleNetworkShow"
        :class="node_block_classlist(node_idx)"
      ></rect>
      <!-- <circle cx="50%" cy="50%" r="25" fill="#409eff" /> -->
      <!-- <path d="M 10 10 C 50 10, 10 50, 50 50" fill="none" stroke="black" stroke-width="2"/> -->
      <!-- <text x="150" y="115" font-size="16" text-anchor="middle" fill="white">RUNOOB SVG TEST</text>
      <rect width="100%" height="100%" stroke="red" stroke-width="4" fill="white" /> -->
    </svg>
    <div class="tree_del_box" :style="{bottom: `${menuBottom}px`}">
      <button id="tree_del_btn" class="tree_btn" @click="handleMenuDel">Delete</button>
      <button id="tree_rec_del_btn" class="tree_btn" @click="handleMenuRecursionDel">Recursion Del</button>
    </div>
  </div>
</template>

<style scoped>
.main_window {
  width: 100%;
  height: 100%;
  /* background-color: antiquewhite; */
  position: relative;
  overflow: hidden;
  z-index: 2;
  vertical-align: middle;
}

.main_window .tree_svg {
  /* background-color: aquamarine; */
  z-index: -1;
  position: absolute;
  border: 1px solid #bcd5fc;
}

.layers_link {
  fill: none;
  stroke: #5b95dd;
  stroke-width: 2;
}

circle {
  /* fill: rgb(224, 240, 244); */
  stroke: #0052D9; /*给画笔设置一个颜色*/
  stroke-width: 1; /*设置线条的宽度*/
  /* stroke-dasharray: 10,10; */
  /* animation: loading-dash 5s ease-in-out infinite; */
}

/* 表示正在被编辑 */
.to_be_del {
  stroke: #ff8c20; /*给画笔设置一个颜色*/
  stroke-width: 3; /*设置线条的宽度*/
  stroke-dasharray: 10,10;
  animation: editing 5s linear infinite;
}

.to_be_save {
  stroke: #0052D9; /*给画笔设置一个颜色*/
  stroke-width: 3; /*设置线条的宽度*/
  stroke-dasharray: 10,10;
  animation: editing 5s ease-in-out infinite;
}

@keyframes editing {
  0% {
    stroke-dashoffset: 0;
  }

  50% {
    stroke-dashoffset: 80px;
  }

  to {
    stroke-dashoffset: 160px;
  }
}

.now_show {
  stroke: #0052D9; /*给画笔设置一个颜色*/
  stroke-width: 2; /*设置线条的宽度*/
  animation: showing 3s ease-in-out infinite;
}

@keyframes showing {
  0% {
    stroke: #bcd5fc;
    stroke-width: 2;
  }

  50% {
    stroke: #daf8ff;
    stroke-width: 2;
  }

  to {
    stroke: #bcd5fc;
    stroke-width: 2;
  }
}

.last_showing_one {
  stroke: #0086d9; /*给画笔设置一个颜色*/
  stroke-width: 2; /*设置线条的宽度*/
  animation: showing_one 3s ease-in-out infinite;
}

@keyframes showing_one {
  0% {
    stroke: #0086d9;
    stroke-width: 3;
  }

  50% {
    stroke: #86e9ff;
    stroke-width: 3;
  }

  to {
    stroke: #0086d9;
    stroke-width: 3;
  }
}
/* 按钮盒 */
.tree_del_box {
  width: 100%;
  height: 30px;
  position: absolute;
  display: flex;
  flex-direction: row;
  background-color: #F6F6F6;

  text-align: center;
  align-items: center;
  /* bottom: 0; */
  transition: all 300ms ease-in-out;
}

.tree_del_box .tree_btn {
  width: calc(50% - 10px);
  height: calc(100% - 6px);
  margin: 10px;

  border: 1px solid #afafaf;
  border-radius: 5px;
  cursor: pointer;
  outline: none;
  transition: all 300ms ease-in-out;
}

.tree_del_box .tree_btn:hover {
  filter: brightness(0.8);
}

.tree_del_box {

}
</style>
