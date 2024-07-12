<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useNetworksData } from '@/stores/networkData';
import { useNetworkSel } from '@/stores/networkSel';
import littleMap from './littleMap.vue';
import L from 'leaflet';
import 'leaflet-draw';
import { useLineEdit } from '@/stores/lineEdit';
// 定义基础类
interface treeNodeStyle {
  left: number,
  top: number,
  border_width: number,
  color: string,
  bgcolor: string
}
interface treeLinkeStyle {
  start: number[],
  end: number[],
  border_width: number,
  dash: boolean,
  color: string
}
interface hslColorObj {
  h: number, s: number, l: number, a: number
}
interface rgbColorObj {
  r: number, g: number, b: number, a: number
}

// 基础信息
const tree_shape_args = {
  horizontal_dis: 50,
  vertical_dis: 0,
  horizontal_padding: 50,
  vertical_padding: 50,
  node_block_half_width: 25,
  node_block_half_height: 25,
  node_block_radius: 25,
}
const color_transition_arr = [
  {r:255, g: 0, b: 0, a: 1}, {r:255, g: 255, b: 255, a: 1}, {r:0, g: 255, b: 0, a: 1}
] as rgbColorObj[]

// 将值转换为颜色
function rgb_color_obj_transition(min_val:number, max_val:number, val:number, colors_transition: rgbColorObj[]) {
  let color_domain_idx = 0
  let std_val = (val-min_val)/(max_val-min_val)
  if (max_val == min_val) std_val = 0.5

  // 判断颜色区间
  const domain_size = colors_transition.length-1
  for (let i=1; i<=domain_size; i++) {
    if (std_val < i/domain_size) break
    else color_domain_idx += 1
  }
  if (color_domain_idx >= domain_size) color_domain_idx = domain_size-1

  // 获取域内颜色
  let domain_std_val = (std_val-color_domain_idx/domain_size)*domain_size
  if (domain_std_val < 0) domain_std_val = 0
  else if (domain_std_val > 1) domain_std_val = 1
  
  const cid = color_domain_idx
  let color_projection = {
    r: colors_transition[cid].r + (colors_transition[cid+1].r-colors_transition[cid].r)*domain_std_val,
    g: colors_transition[cid].g + (colors_transition[cid+1].g-colors_transition[cid].g)*domain_std_val,
    b: colors_transition[cid].b + (colors_transition[cid+1].b-colors_transition[cid].b)*domain_std_val,
    a: colors_transition[cid].a + (colors_transition[cid+1].a-colors_transition[cid].a)*domain_std_val,
  }
  
  return color_projection
}
function rgb_color_transition(min_val:number, max_val:number, val:number, colors_transition: rgbColorObj[]) {
  const color_projection = rgb_color_obj_transition(min_val, max_val, val, colors_transition)
  return "rgba(" + color_projection.r + "," + color_projection.g + "," + color_projection.b + "," + color_projection.a + ")"
}

// 获取网络信息
const networkData = useNetworksData()
const networkSel = useNetworkSel()

// 计算树相关信息
const tree_childs_idxs = ref([] as number[][])
const child_tree_width = ref([] as number[])
const node_top_idx = ref([] as number[])

// 计算svg图片大小
const svg_shape = computed(() => {
  let svg_w = 2*tree_shape_args.horizontal_padding
      + 2*tree_shape_args.node_block_half_width*node_top_idx.value.length
      + 2*tree_shape_args.horizontal_dis*(node_top_idx.value.length-1)
  let svg_h = 2*tree_shape_args.vertical_padding
      + 2*tree_shape_args.node_block_half_height*child_tree_width.value[0]
      + tree_shape_args.vertical_dis*(child_tree_width.value[0]-1)
  if (svg_w == undefined || svg_h == undefined) {
    svg_w = 2*tree_shape_args.horizontal_padding
    svg_h = 2*tree_shape_args.vertical_padding
  }
  return {
    width: svg_w,
    height: svg_h,
  }
})

// 计算节点坐标
const nodes_styles_in_tree = computed(() => {
  // 基础信息
  const midWidth = 4
  const widthRadius = 2
  const bg_opacity = 0.5

  // 开始计算
  const res = [] as treeNodeStyle[]
  
  
  for (let i=0; i<node_top_idx.value.length; i++) {
    const t = node_top_idx.value[i]

    const colorMid = networkData.networksInfoArr[0].avgSpeed
    const colorRadius = Math.max(colorMid-networkData.min_avg_speed, networkData.max_avg_speed-colorMid)

    const nodeColor_obj = rgb_color_obj_transition(colorMid-colorRadius, colorRadius+colorMid,
      networkData.networksInfoArr[i].avgSpeed, color_transition_arr)
    const nodeColor = "rgba(" + nodeColor_obj.r + "," + nodeColor_obj.g + "," + nodeColor_obj.b + "," + nodeColor_obj.a + ")"
    const nodeBGColor = "rgba(" + nodeColor_obj.r + "," + nodeColor_obj.g + "," + nodeColor_obj.b + "," + bg_opacity + ")"

    const widthMid = networkData.networksInfoArr[0].avgFlow
    const widthRadius = Math.max(colorMid-networkData.min_avg_flow, networkData.max_avg_flow-colorMid)
    let nodeWidth = midWidth + widthRadius * (networkData.networksInfoArr[i].avgFlow -
      widthMid)/(2*widthRadius)
    if (widthRadius == 0) nodeWidth = midWidth

    res.push({
      left: tree_shape_args.horizontal_padding +
        i*(tree_shape_args.horizontal_dis+tree_shape_args.node_block_half_width*2),
      top: tree_shape_args.vertical_padding +
        t*(tree_shape_args.vertical_dis+tree_shape_args.node_block_half_height*2),
      border_width: nodeWidth,
      color: nodeColor,
      bgcolor: nodeBGColor
    })
  }
  return res
})

// 计算连接线坐标
const links_styles_in_tree = computed(() => {
  // 基础信息
  const midWidth = 4
  const widthRadius = 2

  // 开始计算
  const res = [] as treeLinkeStyle[]
  for (let i=1; i<networkData.networksFatherIdx.length; i++) {
    // 节点与父节点连接的位置
    const end_pos = [
      nodes_styles_in_tree.value[i].left,
      nodes_styles_in_tree.value[i].top+
        tree_shape_args.node_block_half_height
    ]
    const pt2 = networkData.networksFatherIdx[i]
    const start_pos = [
      nodes_styles_in_tree.value[pt2].left+
        tree_shape_args.node_block_half_width*2,
      nodes_styles_in_tree.value[pt2].top+
        tree_shape_args.node_block_half_height
    ]

    // 计算样式
    const flowRadius = Math.max(Math.abs(networkData.max_diff_avg_flow),
      Math.abs(networkData.min_diff_avg_flow))
    let border_width = midWidth + widthRadius * (networkData.networksInfoArr[i].avgFlow -
      networkData.networksInfoArr[pt2].avgFlow)/(2*flowRadius)
    if (flowRadius == 0) border_width = midWidth
    
    const colorRadius = Math.max(Math.abs(networkData.max_diff_avg_speed),
      Math.abs(networkData.min_diff_avg_speed))
    const colorVal = networkData.networksInfoArr[i].avgSpeed -
      networkData.networksInfoArr[pt2].avgSpeed
    const nodeColor = rgb_color_transition(-colorRadius, +colorRadius, colorVal, color_transition_arr)
    res.push({
      start: start_pos,
      end: end_pos,
      border_width: border_width,
      dash: false,
      color: nodeColor
    })
  }
  return res
})


// 计算节点高度编号
function get_node_top_dis() {
  // 初始化高度数组
  node_top_idx.value = Array(tree_childs_idxs.value.length).fill(0)

  // 开始计算
  const node_to_compute = [0]
  const node_over_dis = [0]
  let lst_len = node_to_compute.length
  let start_idx = 0

  // 从根节点向叶子节点衍生
  while (lst_len-start_idx > 0) {
    for (let i=start_idx; i<lst_len; i++) {
      
      // 取出当前节点
      let now_node_idx = node_to_compute[i]
      
      // 计算当前节点的高度
      node_top_idx.value[now_node_idx] = (child_tree_width.value[now_node_idx]-1)/2+node_over_dis[i]

      // 将子节点插入
      let init_h = node_over_dis[i]
      for (let j=0; j<tree_childs_idxs.value[now_node_idx].length; j++) {
        const now_child_node_idx = tree_childs_idxs.value[now_node_idx][j]
        node_to_compute.push(now_child_node_idx)
        node_over_dis.push(init_h)

        // 更新上方高度
        init_h += child_tree_width.value[now_child_node_idx]
      }
    }
    start_idx = lst_len
    lst_len = node_to_compute.length
  }
}

// 监听树的父节点变化
watch(
  () => networkData.networksFatherIdx,
  (newValue: number[], oldValue: number[]) => {
    // console.log("重新加载tree: ", newValue);
    // 判断数据是否加载完成
    if (newValue.length == 0) return
    
    // 重新设置子节点数组
    child_tree_width.value = []
    tree_childs_idxs.value = []
    for (let i=0; i<newValue.length; i++) {
      child_tree_width.value.push(0)
      tree_childs_idxs.value.push([])
      const tmp_fa_idx = newValue[i]
      if (tmp_fa_idx >= 0) {
        tree_childs_idxs.value[tmp_fa_idx].push(i)
      }
    }

    // 计算各个节点子树的宽度
    for (let i=newValue.length-1; i>=0; i-=1) {
      if (tree_childs_idxs.value[i].length == 0) {
        child_tree_width.value[i] = 1
      } else {
        for (let j=0; j<tree_childs_idxs.value[i].length; j++) {
          child_tree_width.value[i] += child_tree_width.value[tree_childs_idxs.value[i][j]]
        }
      }
    }

    // 计算节点高度编号
    get_node_top_dis()
  },
  {deep: true}
)

// 矩阵相关信息
const matrix_flow_info = ref([] as number[][])
const matrix_speed_info = ref([] as number[][])
const matrix_show_links_global_idx = ref([] as number[])
const matrix_show_links_idx = ref([] as number[][])
const flow_scope = ref([] as number[][])
const speed_scope = ref([] as number[][])
watch(
  () => networkData.networksInfoArr,
  (newValue) => {
    // 保留各个网络的具体取值
    matrix_flow_info.value = new Array(newValue.length)
    matrix_speed_info.value = new Array(newValue.length)
    matrix_show_links_idx.value = new Array(newValue.length)
    matrix_show_links_global_idx.value = new Array(networkData.link_number_matrix).fill(-1)
    for (let i = 0; i < newValue.length; i++) {
      matrix_flow_info.value[i] = new Array(networkData.link_number_matrix).fill(-1)
      matrix_speed_info.value[i] = new Array(networkData.link_number_matrix).fill(-1)
      matrix_show_links_idx.value[i] = new Array(networkData.link_number_matrix).fill(-1)
    }

    for (let i=0; i<newValue.length; i++) {
      for (let j=0; j<newValue[i].links.length; j++) {
        const now_link_global_id = newValue[i].links[j].globalId
        const now_show_idx = networkData.link_sorted_idx[now_link_global_id]
        if (now_show_idx < networkData.link_number_matrix) {
          // 记录flow以及speed信息
          matrix_flow_info.value[i][now_show_idx] = newValue[i].links[j].flow
          matrix_speed_info.value[i][now_show_idx] = newValue[i].links[j].freeFlowTravelTime/newValue[i].links[j].travelTime

          // 记录link id信息
          matrix_show_links_global_idx.value[now_show_idx] = now_link_global_id
          matrix_show_links_idx.value[i][now_show_idx] = j
        }
      }
    }

    // 保留取值范围
    flow_scope.value = new Array(networkData.link_number_matrix)
    speed_scope.value = new Array(networkData.link_number_matrix)

    for (let i=0; i<networkData.links_flow_scope.length; i++) {
      const now_show_idx = networkData.link_sorted_idx[i]
      if (now_show_idx < networkData.link_number_matrix) {
        flow_scope.value[now_show_idx] = networkData.links_flow_scope[i]
        speed_scope.value[now_show_idx] = networkData.links_speed_scope[i]
      }
    }
  },
  {deep: true}
)

// 处理
function handleNodePush(network_idx:number) {
  networkSel.selectNetwork(network_idx)
}

// 加载数据
onMounted(() => {
  // networkData.networksInitialization()
})

const road_name_col_width = 30
const node_space_width = 2*tree_shape_args.node_block_half_width+tree_shape_args.horizontal_dis
const svg_left = road_name_col_width + 2*node_space_width
  -(tree_shape_args.horizontal_padding - tree_shape_args.horizontal_dis/2)
const svg_bg_left = road_name_col_width
  +2*(2*tree_shape_args.node_block_half_width+tree_shape_args.horizontal_dis)
const edit_log_icons = [
  "/static/edits/capacity_up.svg",
  "/static/edits/capacity_down.svg",
  "/static/edits/add_pt.svg",
  "/static/edits/del_pt.svg",
  "/static/edits/add_link.svg",
  "/static/edits/del_link.svg",
  "/static/edits/speed_up.svg",
  "/static/edits/speed_down.svg"
]

// 设置放大缩小以及移动事件
const zoomRat = ref(100)
const matrix_block_left = ref(0)
const matrix_block_top = ref(0)
// 滚轮放大缩小
function handleWheel(e:WheelEvent) {
  if (e.deltaY > 0 && zoomRat.value > 20) {
    zoomRat.value /= 1.2
  } else if (e.deltaY < 0) {
    zoomRat.value *= 1.2
  }
}
// 移动事件
function handleMouseMove(e:MouseEvent) {
  // 当左键被按下
  if (e.buttons == 1) {
    let d_x = e.movementX
    let d_y = e.movementY
    matrix_block_left.value += d_x
    matrix_block_top.value += d_y
  }
}
</script>
<template>
  <div class="main_board">
    <div class="matrix_box"
        @wheel="handleWheel" @mousemove="handleMouseMove">
      <div class="matrix_block"
        :style="{width: svg_shape.width+svg_left + 'px',
        transform: `scale(${zoomRat/100})`, left: matrix_block_left + 'px', top: matrix_block_top + 'px'}">
        <div class="matrix_deck" :style="{height: svg_shape.height+'px', width: svg_shape.width+svg_left + 'px', paddingTop: 0+'px'}">
          <div :style="{height: '100%', width: svg_bg_left+'px'}"></div>
          <div class="svg_node_bgblock"
            v-for="network_edit_logs, network_idx in networkData.all_edit_logs" :key="network_idx"
            :style="{width: node_space_width + 'px', backgroundColor: nodes_styles_in_tree[network_idx].bgcolor}">
            <div class="matrix_deck_element">
              <div class="edit_log_box">
                <span class="edit_log_entity" v-for="edit_log, el_idx in network_edit_logs" :key="el_idx">
                  <img :src="edit_log_icons[edit_log.edit_type]" alt="" srcset="">
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="matrix_part"
          :style="{width: svg_shape.width+svg_left + 'px'}">
          <div class="matrix_col" :style="{width: node_space_width + 'px'}">
            <div class="matrix_element"></div>
            <div class="matrix_element"></div>
            <div class="matrix_element"></div>
          </div>
          <div class="matrix_col" :style="{width: road_name_col_width + 'px'}">
            <div class="matrix_element road_name_box" v-for="link_global_id in matrix_show_links_global_idx"
              :key="link_global_id">Road {{ link_global_id + 1 }}</div>
          </div>
          <div class="matrix_col road_img_show_col" :style="{width: node_space_width + 'px'}">
            <div class="matrix_element matrix_element_with_border" v-for="link_global_id,map_index in matrix_show_links_global_idx"
              :key="link_global_id" >
                <div class="map_box">
                  <littleMap :map_idx= map_index :id="'map'+map_index"></littleMap>
                </div>
              </div>
          </div>
          <div class="matrix_col"
            v-for="network_flow_info, network_idx in matrix_flow_info" :key="network_idx"
            :style="{width: node_space_width + 'px', backgroundColor: nodes_styles_in_tree[network_idx].bgcolor}">
            <div class="matrix_element matrix_element_with_border"
              v-for="link_flow_info, link_show_idx in network_flow_info"
              :key="link_show_idx"></div>
            <!-- <div class="matrix_element matrix_element_with_border"></div>
            <div class="matrix_element matrix_element_with_border"></div> -->
          </div>
        </div>
        <svg version="1.1" class="tree_svg"
          baseProfile="full"
          :width="svg_shape.width" :height="svg_shape.height"
          :style="{left: svg_left + 'px'}"
          xmlns="http://www.w3.org/2000/svg">
          <line v-for="(line_style, line_idx) in links_styles_in_tree" :key="line_idx"
            :x1="line_style.start[0]" :y1="line_style.start[1]" :x2="line_style.end[0]" :y2="line_style.end[1]"
            :style="{stroke:line_style.color, strokeWidth:line_style.border_width}"/>
          <rect v-for="(node_pos, node_idx) in nodes_styles_in_tree" :key="node_idx" :circle_id="node_idx"
            :x="node_pos.left" :y="node_pos.top"
            :style="{strokeWidth: node_pos.border_width, stroke: node_pos.color}"
            :width="tree_shape_args.node_block_half_width*2" :height="tree_shape_args.node_block_half_height*2"
            :rx="tree_shape_args.node_block_radius" :ry="tree_shape_args.node_block_radius" fill="#409eff00"
            @click="handleNodePush(node_idx)"
          ></rect>
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.main_board {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  background-color: grey;
  box-shadow: 2px 5px 5px rgba(255,255,255,0.2);

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-items: center;
  text-align: center;
}


.matrix_box {
  margin-left: auto;
  margin-right: auto;
  width: calc(100% - 18px);
  height: calc(100% - 18px);
  border-radius: 3px;
  background-color: #565656;
  overflow: hidden;
}

.matrix_block {
  width: 500px;
  /* height: 600px; */
  /* background-color: rosybrown; */
  position: relative;
  top: 0px;
}

/* svg图片的样式 */
.tree_svg {
  position: absolute;
  top: 0;
  /* background-color: #0070C1; */
}
/* svg背景板 */
.matrix_deck {
  margin: 0;
  /* background-color: firebrick; */
  
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-items: center;
  text-align: center;
}
.matrix_deck .svg_node_bgblock {
  height: 100%;
}
.matrix_part {
  margin: 0;

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-items: center;
  text-align: center;
}
.matrix_col {
  height: 100%;
}
.matrix_element {
  width: calc(100% - 2px);
  height: 100px;
  /* border-width: 5px; */
  /* border-color: red; */
  /* margin: 0; */
}
.matrix_element.road_name_box {
  writing-mode: vertical-rl;
  user-select: none;
  /* text-orientation: upright; */
}
.matrix_element_with_border,
.matrix_deck_element {
  border: 2px solid #8a8a8a;
}
.matrix_deck_element {
  height: calc(100% - 2px);
  width: calc(100% - 2px);
  position: relative;
  vertical-align: bottom;
  /* vertical-align: bottom; */
}

/* 展示的编辑记录 */
.matrix_deck_element .edit_log_box {
  position: absolute;
  bottom: 0;
  width: 100%;
  /* height: 20px; */
  display: flex;
  flex-direction: row-reverse;
  flex-wrap: wrap;
  background-color: aquamarine;
}
.matrix_deck_element .edit_log_entity {
  display: inline-block;
  width: 20px;
  height: 20px;
  margin: 2px;
  background-color: aliceblue;
  border-radius: 3px;
}
.matrix_deck_element .edit_log_entity img {
  width: 100%;
  height: 100%;
}

/* 地图列 */
.road_img_show_col {
  user-select: none;
}



.map_box{
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  height: 100%;
  border-radius: 3px;
  background-color: aliceblue;
  overflow: hidden;
}

[id^="map"] {
  width: 100%;
  height: 100%;
}

</style>