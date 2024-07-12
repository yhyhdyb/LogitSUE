<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useNetworksData } from '@/stores/networkData'
import { useNetworkSel } from '@/stores/networkSel'
import { useLineEdit } from '@/stores/lineEdit'
import '@/assets/matrix_element.css'
import ThumbnailMap from './ThumbnailMap.vue'
import MatrixGraph from './MatrixGraph.vue'

// 定义基础类
interface treeNodeStyle {
  left: number
  top: number
  border_width: number
  color: string
  bgcolor: string
}
interface treeLinkeStyle {
  start: number[]
  end: number[]
  border_width: number
  dash: boolean
  color: string
}
interface hslColorObj {
  h: number
  s: number
  l: number
  a: number
}
interface rgbColorObj {
  r: number
  g: number
  b: number
  a: number
}

// 基础信息
const tree_shape_args = {
  horizontal_dis: 50,
  vertical_dis: 0,
  horizontal_padding: 50,
  vertical_padding: 50,
  node_block_half_width: 25,
  node_block_half_height: 25,
  node_block_radius: 25
}
const color_transition_arr = [
  { r: 30, g: 255, b: 30, a: 1 },
  { r: 255, g: 255, b: 255, a: 1 },
  { r: 255, g: 30, b: 30, a: 1 }
] as rgbColorObj[]

// 将值转换为颜色
function rgb_color_obj_transition(
  min_val: number,
  max_val: number,
  val: number,
  colors_transition: rgbColorObj[]
) {
  let color_domain_idx = 0
  let std_val = (val - min_val) / (max_val - min_val)
  if (max_val == min_val) std_val = 0.5

  // 判断颜色区间
  const domain_size = colors_transition.length - 1
  for (let i = 1; i <= domain_size; i++) {
    if (std_val < i / domain_size) break
    else color_domain_idx += 1
  }
  if (color_domain_idx >= domain_size) color_domain_idx = domain_size - 1

  // 获取域内颜色
  let domain_std_val = (std_val - color_domain_idx / domain_size) * domain_size
  if (domain_std_val < 0) domain_std_val = 0
  else if (domain_std_val > 1) domain_std_val = 1

  const cid = color_domain_idx
  let color_projection = {
    r:
      colors_transition[cid].r +
      (colors_transition[cid + 1].r - colors_transition[cid].r) * domain_std_val,
    g:
      colors_transition[cid].g +
      (colors_transition[cid + 1].g - colors_transition[cid].g) * domain_std_val,
    b:
      colors_transition[cid].b +
      (colors_transition[cid + 1].b - colors_transition[cid].b) * domain_std_val,
    a:
      colors_transition[cid].a +
      (colors_transition[cid + 1].a - colors_transition[cid].a) * domain_std_val
  }

  return color_projection
}
function rgb_color_transition(
  min_val: number,
  max_val: number,
  val: number,
  colors_transition: rgbColorObj[]
) {
  const color_projection = rgb_color_obj_transition(min_val, max_val, val, colors_transition)
  return (
    'rgba(' +
    color_projection.r +
    ',' +
    color_projection.g +
    ',' +
    color_projection.b +
    ',' +
    color_projection.a +
    ')'
  )
}

// 获取网络信息
const networkData = useNetworksData()
const networkSel = useNetworkSel()
const lineEditData = useLineEdit()

// 计算树相关信息
const tree_childs_idxs = ref([] as number[][])
const child_tree_width = ref([] as number[])
const node_top_idx = ref([] as number[])

// 计算svg图片大小
const svg_shape = computed(() => {
  let svg_w =
    2 * tree_shape_args.horizontal_padding +
    2 * tree_shape_args.node_block_half_width * node_top_idx.value.length +
    2 * tree_shape_args.horizontal_dis * (node_top_idx.value.length - 1)
  let svg_h =
    2 * tree_shape_args.vertical_padding +
    2 * tree_shape_args.node_block_half_height * child_tree_width.value[0] +
    tree_shape_args.vertical_dis * (child_tree_width.value[0] - 1)
  if (svg_w == undefined || svg_h == undefined) {
    svg_w = 2 * tree_shape_args.horizontal_padding
    svg_h = 2 * tree_shape_args.vertical_padding
  }
  return {
    width: svg_w+30,
    height: svg_h,
  }
})

// 计算节点坐标
const nodes_styles_in_tree = computed(() => {
  // 基础信息
  const bg_opacity = 0.3

  // 开始计算
  const res = [] as treeNodeStyle[]

  for (let i = 0; i < node_top_idx.value.length; i++) {
    const colorMid = networkData.networksInfoArr[0].costSum
    const colorRadius = Math.max(
      colorMid - networkData.min_cost_sum,
      networkData.max_cost_sum - colorMid
    )
    const t = node_top_idx.value[i]

    const nodeColor_obj = rgb_color_obj_transition(
      colorMid - colorRadius,
      colorRadius + colorMid,
      networkData.networksInfoArr[i].costSum,
      color_transition_arr
    )
    const nodeColor =
      'rgba(' +
      nodeColor_obj.r +
      ',' +
      nodeColor_obj.g +
      ',' +
      nodeColor_obj.b +
      ',' +
      nodeColor_obj.a +
      ')'
    const bg_color_transition_arr = [
      { r: 130, g: 255, b: 130, a: 1 },
      { r: 255, g: 255, b: 255, a: 1 },
      { r: 255, g: 130, b: 130, a: 1 }
    ]
    const nodebg_Color_obj = rgb_color_obj_transition(
      colorMid - colorRadius,
      colorRadius + colorMid,
      networkData.networksInfoArr[i].costSum,
      bg_color_transition_arr
    )
    const nodeBGColor =
      'rgba(' +
      nodebg_Color_obj.r +
      ',' +
      nodebg_Color_obj.g +
      ',' +
      nodebg_Color_obj.b +
      ',' +
      bg_opacity +
      ')'

    res.push({
      left:
        tree_shape_args.horizontal_padding +
        i * (tree_shape_args.horizontal_dis + tree_shape_args.node_block_half_width * 2),
      top:
        tree_shape_args.vertical_padding +
        t * (tree_shape_args.vertical_dis + tree_shape_args.node_block_half_height * 2),
      border_width: 4,
      color: nodeColor,
      bgcolor: nodeBGColor
    })
  }
  return res
})

// 计算连接线坐标
const links_styles_in_tree = computed(() => {
  // 开始计算
  const res = [] as treeLinkeStyle[]
  for (let i = 1; i < networkData.networksFatherIdx.length; i++) {
    // 节点与父节点连接的位置
    const end_pos = [
      nodes_styles_in_tree.value[i].left,
      nodes_styles_in_tree.value[i].top + tree_shape_args.node_block_half_height
    ]
    const pt2 = networkData.networksFatherIdx[i]
    const start_pos = [
      nodes_styles_in_tree.value[pt2].left + tree_shape_args.node_block_half_width * 2,
      nodes_styles_in_tree.value[pt2].top + tree_shape_args.node_block_half_height
    ]

    // 计算样式
    const colorRadius = Math.max(
      Math.abs(networkData.max_diff_cost_sum),
      Math.abs(networkData.min_diff_cost_sum)
    )
    const colorVal =
      networkData.networksInfoArr[i].costSum - networkData.networksInfoArr[pt2].costSum
    const nodeColor = rgb_color_transition(
      -colorRadius,
      +colorRadius,
      colorVal,
      color_transition_arr
    )
    res.push({
      start: start_pos,
      end: end_pos,
      border_width: 4,
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
  while (lst_len - start_idx > 0) {
    for (let i = start_idx; i < lst_len; i++) {
      // 取出当前节点
      let now_node_idx = node_to_compute[i]

      if (
        now_node_idx >= networkData.networksInfoArr.length ||
        now_node_idx >= tree_childs_idxs.value.length
      )
        return

      // 计算当前节点的高度
      node_top_idx.value[now_node_idx] =
        (child_tree_width.value[now_node_idx] - 1) / 2 + node_over_dis[i]

      // 将子节点插入
      let init_h = node_over_dis[i]
      for (let j = 0; j < tree_childs_idxs.value[now_node_idx].length; j++) {
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
  () => networkData.networksInfoArr,
  () => {
    // 判断数据是否加载完成
    if (networkData.networksFatherIdx.length == 0) return

    // 重新设置子节点数组
    child_tree_width.value = []
    tree_childs_idxs.value = []

    for (let i = 0; i < networkData.networksFatherIdx.length; i++) {
      child_tree_width.value.push(0)
      tree_childs_idxs.value.push([])
      const tmp_fa_idx = networkData.networksFatherIdx[i]
      if (tmp_fa_idx >= 0) {
        tree_childs_idxs.value[tmp_fa_idx].push(i)
      }
    }

    // 计算各个节点子树的宽度
    for (let i = networkData.networksFatherIdx.length - 1; i >= 0; i -= 1) {
      if (tree_childs_idxs.value[i].length == 0) {
        child_tree_width.value[i] = 1
      } else {
        for (let j = 0; j < tree_childs_idxs.value[i].length; j++) {
          child_tree_width.value[i] += child_tree_width.value[tree_childs_idxs.value[i][j]]
        }
      }
    }

    // 计算节点高度编号
    get_node_top_dis()
  },
  { deep: true }
)

// 删除某个路网
async function del_network_node_recursion(e: MouseEvent, network_idx: number) {
  e.preventDefault()
  const networks_to_del = [network_idx]
  let now_pos = 0
  while (now_pos < networks_to_del.length) {
    const now_network = networks_to_del[now_pos]
    for (let i = 0; i < tree_childs_idxs.value[now_network].length; i++) {
      networks_to_del.push(tree_childs_idxs.value[now_network][i])
      // console.log("new del: ", tree_childs_idxs.value);
      
    }
    now_pos++
    // console.log("now pos: ", networks_to_del.length, ", ", now_pos);
    
  }
  // console.log("del networks: ", networks_to_del);
  // console.log("tree: ", tree_childs_idxs.value);
  
  
  networkSel.deleteNetworks(networks_to_del)
  await networkData.networkRecursionDelete(networks_to_del)
}

// 获取某个网络某个路段信息
function get_network_info(network_idx: number, show_link_idx: number) {
  const link_global_idx = networkData.sel_links_global_idx[show_link_idx]
  const link_idx_in_network = networkData.sel_links_networks_idx[network_idx][show_link_idx]
  if (
    link_idx_in_network == -1 ||
    link_idx_in_network > networkData.networksInfoArr[network_idx].links.length
  ) {
    console.log('[link click] 该路段不存在')
  } else {
    const link = networkData.networksInfoArr[network_idx].links[link_idx_in_network]
    console.log(
      '[link click] ID(network) = ',
      link_idx_in_network,
      ', freeFlowTravelTime: ',
      link.freeFlowTravelTime,
      ', capacity: ',
      link.capacity,
      ', travelTime: ',
      link.travelTime,
      ', flow: ',
      link.flow
    )
  }
}
function light_up_link(show_link_idx: number) {
  const link_global_idx = networkData.sel_links_global_idx[show_link_idx]
  // 高亮显示该路段
  let link_now_idx = -1
  const now_network_idx = networkSel.last_sel_network_id
  if (now_network_idx == -1) {
    return
  }
  for (let i = 0; i < networkData.networksInfoArr[now_network_idx].links.length; i++) {
    if (networkData.networksInfoArr[now_network_idx].links[i].globalId == link_global_idx) {
      link_now_idx = i
      break
    }
  }
  if (link_now_idx == -1) {
    return
  }
  lineEditData.lineIdx = link_now_idx
  lineEditData.link_to_lightup = !lineEditData.link_to_lightup
}
let light_up_timer = 0
function handleMouseInMatrixLink(show_link_idx = -1) {
  clearTimeout(light_up_timer)
  if (show_link_idx == -1) return
  light_up_timer = setTimeout(() => {
    light_up_link(show_link_idx)
  }, 500)
}

// function txt_box_bottom(network_idx: number, show_link_idx: number, val_type:number) {
//   const is_highlight = network_idx == highlight_network.value &&
//     show_link_idx == highlight_link.value &&
//     matrix_element_type.value!=0
//   if (!is_highlight) return 0

//   // 判断位置是否匹配，是否在左右对应的bar上
//   if (matrix_element_type.value <= 4) {
//     if (val_type >= 3) return 0
//     else if (matrix_element_type.value == 1) {
//       return matrix_element_network_val(network_idx, show_link_idx, 1)
//     } else if (matrix_element_type.value == 2) {
//       return matrix_element_network_val(network_idx, show_link_idx, 2) as number -1
//     } else if (matrix_element_type.value == 3) {
//       return matrix_element_network_val(network_idx, show_link_idx, 0)
//     } else if (matrix_element_type.value == 4) {
//       return matrix_element_network_val(network_idx, show_link_idx, 1)
//     } else return 0
//   } else {
//     if (val_type < 3) return 0
//     else if (matrix_element_type.value == 5) {
//       return matrix_element_network_val(network_idx, show_link_idx, 4)
//     } else if (matrix_element_type.value == 6) {
//       return matrix_element_network_val(network_idx, show_link_idx, 5) as number -1
//     } else if (matrix_element_type.value == 7) {
//       return matrix_element_network_val(network_idx, show_link_idx, 3)
//     } else if (matrix_element_type.value == 8) {
//       return matrix_element_network_val(network_idx, show_link_idx, 4)
//     } else return 0
//   }

// }
// function txt_box_content(network_idx: number, show_link_idx: number, val_type:number) {
//   const is_highlight = network_idx == highlight_network.value && show_link_idx == highlight_link.value
//   if (!is_highlight) return ""
//   // 判断展示什么内容
//   const link_global_idx = matrix_show_links_global_idx.value[show_link_idx]
//   const link_idx_in_network = matrix_show_links_idx.value[network_idx][show_link_idx]
//   if (link_idx_in_network == -1 || link_idx_in_network > networkData.networksInfoArr[network_idx].links.length) {
//     // 路段不存在
//     return ""
//   }
//   const now_link = networkData.networksInfoArr[network_idx].links[link_idx_in_network]
//   if (val_type < 3) {
//     if (matrix_element_type.value == 1) {
//       return formatNumber(now_link.flow/now_link.capacity)
//     } else if (matrix_element_type.value == 2) {
//       return formatNumber(networkData.all_flow_ratio_scope[2])
//     } else if (matrix_element_type.value == 3) {
//       return formatNumber(now_link.capacity)
//     } else if (matrix_element_type.value == 4) {
//       return formatNumber(now_link.flow)
//     } else return ""
//   } else {
//     if (matrix_element_type.value == 5) {
//       return formatNumber(now_link.freeFlowTravelTime/now_link.travelTime)
//     } else if (matrix_element_type.value == 6) {
//       return formatNumber(networkData.all_speed_scope[2])
//     } else if (matrix_element_type.value == 7) {
//       return formatNumber(now_link.travelTime)
//     } else if (matrix_element_type.value == 8) {
//       return formatNumber(now_link.freeFlowTravelTime)
//     } else return ""
//   }
// }
// function matrix_bar_content(network_idx: number, show_link_idx: number, val_type:number) {
//   const is_highlight = network_idx == highlight_network.value && show_link_idx == highlight_link.value
//   if (!is_highlight) return ""
//   // 判断展示什么内容
//   const link_global_idx = matrix_show_links_global_idx.value[show_link_idx]
//   const link_idx_in_network = matrix_show_links_idx.value[network_idx][show_link_idx]
//   if (link_idx_in_network == -1 || link_idx_in_network > networkData.networksInfoArr[network_idx].links.length) {
//     // 路段不存在
//     return ""
//   }
//   const now_link = networkData.networksInfoArr[network_idx].links[link_idx_in_network]
//   if (matrix_element_type.value == 1 && val_type == 1) {
//     return formatNumber(now_link.flow/now_link.capacity)
//   } else if (matrix_element_type.value == 2 && val_type == 2) {
//     return formatNumber(networkData.all_flow_ratio_scope[2])
//   } else if (matrix_element_type.value == 3 && val_type == 0) {
//     return formatNumber(now_link.capacity)
//   } else if (matrix_element_type.value == 4 && val_type == 1) {
//     return formatNumber(now_link.flow)
//   } else if (matrix_element_type.value == 5 && val_type == 4) {
//     return formatNumber(now_link.freeFlowTravelTime/now_link.travelTime)
//   } else if (matrix_element_type.value == 6 && val_type == 5) {
//     return formatNumber(networkData.all_speed_scope[2])
//   } else if (matrix_element_type.value == 7 && val_type == 3) {
//     return formatNumber(now_link.travelTime)
//   } else if (matrix_element_type.value == 8 && val_type == 4) {
//     return formatNumber(now_link.freeFlowTravelTime)
//   }
// }

// 处理
function handleNodePush(network_idx: number) {
  networkSel.selectNetwork(network_idx)
}


const road_name_col_width = 30
const node_space_width = 2 * tree_shape_args.node_block_half_width + tree_shape_args.horizontal_dis
const svg_left =
  road_name_col_width +
  2 * node_space_width -
  (tree_shape_args.horizontal_padding - tree_shape_args.horizontal_dis / 2)
const svg_bg_left =
  road_name_col_width +
  2 * (2 * tree_shape_args.node_block_half_width + tree_shape_args.horizontal_dis)
const edit_log_icons = [
  '/static/edits/capacity_up.svg',
  '/static/edits/capacity_down.svg',
  '/static/edits/add_pt.svg',
  '/static/edits/del_pt.svg',
  '/static/edits/add_link.svg',
  '/static/edits/del_link.svg',
  '/static/edits/speed_up.svg',
  '/static/edits/speed_down.svg'
]

// 设置放大缩小以及移动事件
const zoomRat = ref(100)
const matrix_block_left = ref(0)
const matrix_block_top = ref(0)
// 滚轮放大缩小
function handleWheel(e: WheelEvent) {
  // e.
  const touch_board = document.getElementById('matrix_put_area') as HTMLElement
  const touch_board_pos = touch_board.getBoundingClientRect()
  const touch_board_cx = touch_board_pos.left + touch_board_pos.width / 2
  const touch_board_cy = touch_board_pos.top + touch_board_pos.height / 2
  const mouse_in_top = touch_board_cx - e.clientY
  const mouse_in_left = touch_board_cy - e.clientX
  // console.log("mouse_dis: ", mouse_in_top, ", ", mouse_in_left);
  
  
  if (e.deltaY > 0 && zoomRat.value > 20) {
    // 以鼠标为中心位移
    // matrix_block_top.value += mouse_in_top/6/(zoomRat.value/100)
    // matrix_block_left.value += mouse_in_left/6/(zoomRat.value/100)
    zoomRat.value /= 1.2
  } else if (e.deltaY < 0) {
    // 以鼠标为中心位移
    zoomRat.value *= 1.2
    // matrix_block_top.value -= mouse_in_top*0.2/(zoomRat.value/100*1.44)
    // matrix_block_left.value -= mouse_in_left*0.2/(zoomRat.value/100*1.44)
  }
}
// 移动事件
let matrix_move_start = [-1, -1]
function matrixMoveStart(e: MouseEvent) {
  matrix_move_start = [e.clientX, e.clientY]
  if (matrix_move_start[0] == -1 && matrix_move_start[1] == -1)
    matrix_move_start = [-1.1,-1.1]
}
function matrixMoveEnd(e: MouseEvent) {
  matrix_move_start = [-1, -1]
}
function handleMouseMove(e:MouseEvent) {
  if (matrix_move_start[0] == -1 && matrix_move_start[1] == -1) return
  // 当左键被按下
  if (e.buttons == 1) {
    e.preventDefault()
    
    matrix_block_left.value += e.clientX-matrix_move_start[0]
    matrix_block_top.value += e.clientY-matrix_move_start[1]
    matrix_move_start = [e.clientX, e.clientY]
    // let d_x = e.movementX
    // let d_y = e.movementY
    // matrix_block_left.value += d_x
    // matrix_block_top.value += d_y
  }
}

// 是否选择网络状态作为过滤条件
const networks_as_filter_icons = (now_state: boolean) => {
  if (now_state) {
    return "/static/matrix_btns/sel_filter.svg"
  } else return "/static/matrix_btns/un_sel.svg"
}
// 选择是否要将link置顶
const link_if_alt_top = (link_idx: number) => {
  if (link_idx<0 || link_idx>networkData.linksAltTop.length) {
    return "/static/matrix_btns/un_sel.svg"
  }
  if (networkData.linksAltTop[link_idx]) {
    return "/static/matrix_btns/sel_top.svg"
  } else return "/static/matrix_btns/un_sel.svg"
}
// 切换link是否置顶
function shift_link_alt_to_top(link_global_id: number) {
  if (link_global_id < networkData.linksAltTop.length && link_global_id>=0) {
    networkData.linksAltTop[link_global_id] = !networkData.linksAltTop[link_global_id]
  }
}

</script>
<template>
  <div class="main_board">
    <div class="matrix_box" id="matrix_show_area"
      @mousedown="matrixMoveStart" @mouseleave="matrixMoveEnd"
      @mouseup="matrixMoveEnd"
      @wheel="handleWheel" @mousemove="handleMouseMove">
      <div class="matrix_block" id="matrix_put_area"
        :style="{width: svg_shape.width+svg_left + 'px',
        transform: `scale(${zoomRat/100})`, left: matrix_block_left + 'px', top: matrix_block_top + 'px'}">
        <div class="matrix_state__sel_bar" :style="{width: svg_shape.width+svg_left + 'px', paddingTop: 0+'px'}">
          <div :style="{height: '100%', width: svg_bg_left+'px'}"></div>
          <div class="svg_node_selblock" :style="{height: '100%', width: node_space_width+'px'}" 
            v-for="network_as_filter, network_idx in networkData.networksAsFilter" :key="network_idx">
            <span class="state_filter_sel_btn"
              @click="networkData.shift_network_as_filter_state(network_idx)">
              <img :src="networks_as_filter_icons(network_as_filter)" alt="" srcset="">
            </span>
          </div>
        </div>
        <div class="matrix_deck" :style="{height: svg_shape.height+'px', width: svg_shape.width+svg_left + 'px', paddingTop: 0+'px'}">
          <div :style="{height: '100%', width: svg_bg_left+'px'}"></div>
          <div class="svg_node_bgblock"
            v-for="network_edit_logs, network_idx in networkData.all_edit_logs" :key="network_idx"
            :style="{width: node_space_width + 'px', backgroundColor: nodes_styles_in_tree[network_idx].bgcolor}">
            <div class="matrix_deck_element">
              <div class="edit_log_box">
                <span
                  class="edit_log_entity"
                  v-for="(edit_log, el_idx) in network_edit_logs"
                  :key="el_idx"
                  :class="{ this_edit: edit_log.edit_on_this }"
                >
                  <img :src="edit_log_icons[edit_log.edit_type - 1]" alt="" srcset="" />
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="matrix_part" :style="{ width: svg_shape.width + svg_left + 'px' }">
          <div class="matrix_col" :style="{ width: node_space_width + 'px' }">
            <div
              class="matrix_element"
              v-for="link_global_id in networkData.sel_links_global_idx"
              style="border: 2px solid transparent;"
              :key="link_global_id"
            ></div>
          </div>
          <div class="matrix_col" :style="{ width: road_name_col_width + 'px' }">
            <div
              class="matrix_element road_name_box"
              v-for="link_global_id in networkData.sel_links_global_idx"
              :key="link_global_id"
            >
              Road {{ link_global_id + 1 }}
            </div>
          </div>
          <div class="matrix_col road_img_show_col" :style="{ width: node_space_width + 'px' }">
            <div
              class="matrix_element matrix_element_with_border"
              v-for="(link_global_id, show_idx) in networkData.sel_links_global_idx"
              :key="link_global_id"
              @mouseenter="handleMouseInMatrixLink(show_idx)"
              @mouseleave="handleMouseInMatrixLink()"
            >
              <ThumbnailMap :thumb_map_idx="show_idx"></ThumbnailMap>
            </div>
          </div>
          <div
            class="matrix_col"
            v-for="(network_flow_info, network_idx) in networkData.sel_links_networks_idx"
            :key="network_idx"
            :style="{
              width: node_space_width + 'px',
              backgroundColor: nodes_styles_in_tree[network_idx].bgcolor
            }"
          >
            <div
              class="matrix_element matrix_element_with_border"
              v-for="(link_flow_info, link_show_idx) in network_flow_info"
              :key="link_show_idx"
              @mouseenter="handleMouseInMatrixLink(link_show_idx)"
              @mouseleave="handleMouseInMatrixLink()"
              @click="get_network_info(network_idx, link_show_idx)"
            >
              <MatrixGraph :network_idx="network_idx" :show_link_idx="link_show_idx"></MatrixGraph>
            </div>
          </div>
          <div class="matrix_col links_alt_top_btns_box">
            <div class="link_alt_top_btn_box"
              v-for="link_global_id, show_idx in networkData.sel_links_global_idx" :key="show_idx">
              <span class="links_alt_top_btn" @click="shift_link_alt_to_top(link_global_id)">
                <img :src="link_if_alt_top(link_global_id)" alt="" srcset="">
              </span>
            </div>
          </div>
        </div>
        <svg
          version="1.1"
          class="tree_svg"
          baseProfile="full"
          :style="{
            left: svg_left + 'px',
            width: svg_shape.width + 'px',
            height: svg_shape.height + 'px'
          }"
          xmlns="http://www.w3.org/2000/svg"
        >
          <line
            v-for="(line_style, line_idx) in links_styles_in_tree"
            :key="line_idx"
            :x1="line_style.start[0]"
            :y1="line_style.start[1]"
            :x2="line_style.end[0]"
            :y2="line_style.end[1]"
            :style="{ stroke: line_style.color, strokeWidth: line_style.border_width }"
          />
          <rect
            v-for="(node_pos, node_idx) in nodes_styles_in_tree"
            :key="node_idx"
            :circle_id="node_idx"
            :class="{ rect_sel2show: networkSel.last_sel_network_id == node_idx }"
            :x="node_pos.left"
            :y="node_pos.top"
            :style="{ strokeWidth: node_pos.border_width, stroke: node_pos.color }"
            :width="tree_shape_args.node_block_half_width * 2"
            :height="tree_shape_args.node_block_half_height * 2"
            :rx="tree_shape_args.node_block_radius"
            :ry="tree_shape_args.node_block_radius"
            fill="#409eff00"
            @click="handleNodePush(node_idx)"
            @contextmenu="del_network_node_recursion($event, node_idx)"
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
  /* border-radius: 8px; */
  background-color: grey;
  /* box-shadow: 2px 5px 5px rgba(255, 255, 255, 0.2); */

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-items: center;
  text-align: center;
}

/* 被选中的路网特殊效果 */
@keyframes dash_moving {
  0% {
    /* transform: rotate(0deg); */
    stroke-dashoffset: 0px;
  }
  100% {
    /* transform: rotate(360deg); */
    stroke-dashoffset: 120px;
  }
}

.rect_sel2show {
  border-style: dashed;
  stroke-dasharray: 6;
  animation: dash_moving 5s linear infinite;
}

.matrix_box {
  margin-left: auto;
  margin-right: auto;
  width: calc(100% - 18px);
  height: calc(100% - 18px);
  border-radius: 3px;
  background-color: #121212;
  overflow: hidden;

  z-index: 3;
}

.matrix_block {
  width: 500px;
  /* height: 600px; */
  /* background-color: rosybrown; */
  position: relative;
  top: 0px;
  /* transition: all 0.05s ease; */

  z-index: 1;
}

.matrix_block * {
  user-select: none;
}

/* svg图片的样式 */
.tree_svg {
  position: absolute;
  top: 30px;
  transition: all 0.3s ease;
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
.matrix_deck .svg_node_bgblock,
.matrix_state__sel_bar .svg_node_selblock {
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
  border: 2px solid transparent;
}
.matrix_element_with_border,
.matrix_deck_element {
  border: 2px solid #303030;
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
  /* background-color: aquamarine; */
}
.matrix_deck_element .edit_log_entity {
  display: inline-block;
  width: 20px;
  height: 20px;
  margin: 2px;
  background-color: #adadad;
  border-radius: 3px;
}
.matrix_deck_element .edit_log_entity.this_edit {
  background-color: #fafafa;
}
.matrix_deck_element .edit_log_entity img {
  width: 100%;
  height: 100%;
  user-select: none;
}

/* 地图列 */
.road_img_show_col {
  user-select: none;
}

/* 是否选择状态进行过滤 */
.matrix_state__sel_bar {
  height: 30px;

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-items: center;
  text-align: center;
}
.svg_node_selblock {
  text-align: right;
  border: 2px solid transparent;
}
.svg_node_selblock .state_filter_sel_btn {
  display: inline-block;
  padding: 2px;
  padding-right: 0;
  height: 26px;
  width: 26px;

  user-select: none;
  cursor: pointer;
}
.svg_node_selblock .state_filter_sel_btn img {
  width: 100%;
  height: 100%;
}
.svg_node_selblock .state_filter_sel_btn:hover img {
  filter: brightness(0.8);
}
/* 是否置顶道路 */
.links_alt_top_btns_box {
  width: 30px;
}
.links_alt_top_btns_box .link_alt_top_btn_box {
  height: 100px;
  width: 100%;
  border: 2px solid transparent;
}
.links_alt_top_btns_box .links_alt_top_btn {
  display: inline-block;
  width: 26px;
  height: 26px;
  padding: 2px;
  padding-top: 0;
  cursor: pointer;
  user-select: none;
}
.links_alt_top_btns_box .links_alt_top_btn img {
  width: 100%;
  height: 100%;
}
.links_alt_top_btns_box .links_alt_top_btn:hover img {
  filter: brightness(0.8);
}
</style>
