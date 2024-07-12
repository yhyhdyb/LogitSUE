<script setup lang="ts">
import L, { polyline } from 'leaflet';
import 'leaflet-draw';
import { useNetworksData } from '@/stores/networkData';
import { useNetworkSel } from '@/stores/networkSel';
import { useLineEdit } from '@/stores/lineEdit';
import "@/assets/new_link_menu.css"
import "@/assets/edit_link_menu.css"
import "@/assets/new_node_menu.css"
import { computed, onMounted, ref } from 'vue';
import { watch } from 'vue';
// import { icon } from 'leaflet';

const networkData = useNetworksData()
const networkSelData = useNetworkSel()
const lineEditData = useLineEdit()
let dots_adjacency_matrix = [] as boolean[][]
let now_new_line:L.Polyline
let map: L.Map

// 修改的线类型
class SelectablePolyline extends L.Polyline {
  isSelected: boolean;
  former_idxs: number[];
  new_idx: number;

  constructor(latlngs: L.LatLngExpression[] | L.LatLngExpression[][], former_idxs: number[], new_idx:number, options?: L.PolylineOptions) {
    super(latlngs, options);
    this.isSelected = false;
    this.former_idxs = former_idxs
    this.new_idx = new_idx

    // 设置右键监听
    this.on('contextmenu', function (e) {
      // 阻止默认的右键菜单
      e.originalEvent.preventDefault();
      // e.originalEvent
      handleLinkClick(e.originalEvent, former_idxs[0])
    })

    // 添加点击事件监听器
    this.on('click', (e: L.LeafletMouseEvent) => {
      this.isSelected = !this.isSelected;
      const nodes_in_link = this.getLatLngs()
      
      // 设置道路信息
      if (lineEditData.editState == 0 || lineEditData.editState == 2) {
        if (former_idxs[0] == -1) {
          lineEditData.editState = 1
        }
        else {
          lineEditData.editState = 2
          const now_network_idx = networkSelData.last_sel_network_id
          lineEditData.networkIdx = now_network_idx
          lineEditData.newCapacity = networkData.networksInfoArr[now_network_idx].links[former_idxs[0]].capacity
          lineEditData.newFreeFlowTravelTime = networkData.networksInfoArr[now_network_idx].links[former_idxs[0]].freeFlowTravelTime
          lineEditData.lineIdx = former_idxs[0]
        }
        // 显示路段信息
        
      }
    });
  }
}
// 修改的点的类型
class SelectableNode extends L.CircleMarker {
  isSelected: boolean
  former_idxs: number[]
  new_idx: number

  constructor(latlng: L.LatLngExpression, former_idxs: number[], new_idx: number, options?: L.CircleMarkerOptions) {
    super(latlng, options)
    this.isSelected = false
    this.former_idxs = former_idxs
    this.new_idx = new_idx
    const _this = this
    

    // 设置右键监听
    this.on('contextmenu', function (e) {
      // 阻止默认的右键菜单
      e.originalEvent.preventDefault();
      // e.originalEvent
      const thisElement = _this.getElement() as HTMLElement
      thisElement.classList.add('custom-class');
      handleNodeClick(e.originalEvent, former_idxs[0])
    })

    // Add click event listener
    this.on('click', (e) => {
      this.isSelected = !this.isSelected

      // 开始创建线段
      if (lineEditData.editState == 1 && map != undefined && former_idxs[0]!=-1) {
        if (lineEditData.startNodeIdx == -1) {
          // 获取当前选中的网络
          const now_show_network_idx = networkSelData.last_sel_network_id
          if (now_show_network_idx == -1) return

          // 判断是否需要删除之前的路段
          if (now_new_line!=undefined && map.hasLayer(now_new_line)) {
            map.removeLayer(now_new_line)
          } 

          // 保存需要新建的路段的信息
          const startNode = networkData.networksInfoArr[now_show_network_idx].nodes[former_idxs[0]]
          lineEditData.networkIdx = now_show_network_idx
          lineEditData.startNodeIdx = former_idxs[0]
          lineEditData.startNodePos = [startNode.lat, startNode.lon]
          now_new_line = L.polyline([[lineEditData.startNodePos[0], lineEditData.startNodePos[1]]], {
            // color: '#1FD86D55',//线的颜色
            color: '#808080',
            fillOpacity: 0.5,
            weight: 6, //线的粗细
          }).addTo(map)
          now_new_line.bringToBack()
          
          // 开始鼠标跟随
          map.on('mousemove', onMouseMove)
        } else if (lineEditData.startNodeIdx == former_idxs[0]) {
          lineEditData.editState = 0
          map.off('mousemove', onMouseMove)
        } else if (lineEditData.endNodeIdx == -1) {
          const now_show_network_idx = networkSelData.last_sel_network_id
          const end_node = networkData.networksInfoArr[now_show_network_idx].nodes[former_idxs[0]]
          lineEditData.endNodeIdx = former_idxs[0]
          now_new_line.setLatLngs([[lineEditData.startNodePos[0], lineEditData.startNodePos[1]], [end_node.lat, end_node.lon]])
          now_new_line.redraw()
          map.off('mousemove', onMouseMove)
        } else {
          lineEditData.startDraw()
        }
      }

      // Change color based on isSelected value
      if (this.isSelected) {
        this.setStyle({ color: '#ff0000' }) // Color when selected
      } else {
        this.setStyle({ color: '#0070C1' }) // Color when not selected
      }
    });
    this.on('mouseover', () => {
      // console.log("in!!!", former_idxs[0]);
      
    })
  }
}

function get_links(network_idx:number) {
  // 判断图层编号是否合法
  if (network_idx<0 || network_idx>=networkData.networksInfoArr.length) {
    network_idx = 0
  }
  const links_arr = [] as ((number[])[])[]
  const nodes_in_network = networkData.networksInfoArr[network_idx].nodes
  for (let i=0; i<networkData.networksInfoArr[network_idx].links.length; i++) {
    let link_data = networkData.networksInfoArr[network_idx].links[i]
    const now_link = [] as (number[])[]
    const start_point_id = link_data.pInNode
    const end_point_id = link_data.pOutNode
    now_link.push([
      nodes_in_network[start_point_id].lat,
      nodes_in_network[start_point_id].lon,
    ])
    now_link.push([
      nodes_in_network[end_point_id].lat,
      nodes_in_network[end_point_id].lon,
    ])
    links_arr.push(now_link)
  }
  return links_arr
}

watch(
  () => lineEditData.editState,
  (newValue: number, oldValue: number) => {
    if (newValue == 0 && oldValue == 1) {
      if (now_new_line != undefined)
        map.removeLayer(now_new_line)
    }
  }
)

watch(
  () => networkSelData.last_sel_network_id,
  () => {
    if (lineEditData.editState == 1) {
      lineEditData.startDraw()
    }
  }
)

const creategroup = L.featureGroup([])
const dots_in_map = new Array<SelectableNode>()
const links_in_map = new Array<SelectablePolyline>()
const link_clicked = ref(-1) // 被点击了的路段

// 鼠标移动事件监听器
function onMouseMove(e: L.LeafletMouseEvent) {
  const lat = e.latlng.lat;
  const lng = e.latlng.lng;
  
  if (lineEditData.editState == 1 && map != undefined && lineEditData.startNodeIdx != -1) {
    now_new_line.setLatLngs([[lineEditData.startNodePos[0], lineEditData.startNodePos[1]], [lat, lng]])
    now_new_line.redraw()
  }
}

// 将原来的节点和线段删除
function rmFormerLinesAndDots() {
  if (map == undefined) return
  // 删除节点
  for (let i=dots_in_map.length-1; i>=0; i--) {
    if (dots_in_map[i]) {
      map.removeLayer(dots_in_map[i])
    }
  }
  // 删除线段
  for (let i=links_in_map.length-1; i>=0; i--) {
    if (links_in_map[i]) {
      map.removeLayer(links_in_map[i])
    }
  }
  dots_in_map.length = 0
  links_in_map.length = 0
}
// 画上节点和线段
function drawLinesAndDots() {
  if (map == undefined) return
  
  for (let i=links_in_map.length-1; i>=0; i--) {
    links_in_map[i].addTo(map);
  }
  for (let i=dots_in_map.length-1; i>=0; i--) {
    dots_in_map[i].addTo(map);
  }
}

// 记录原始点位信息和id
let dots_pos = new Array<number[]>()
let links_pos = new Array<number[][]>()
let dots_in_links = new Array<number[]>()
let dots_flow_sum = new Array<number>()
let dots_a_idx = new Array<number>()
let dots_b_idx = new Array<number>()
let link_a_idx = new Array<number>()
let link_b_idx = new Array<number>()
let link_flow_ratio = new Array<number>()
let link_speed_ratio = new Array<number>()
const map_zoom_ratio = ref(12)

// 展示的图片的speed和flow的取值范围
let speed_scope = [] as number[]
let flow_scope = [0,1] as number[]
let fftt_dimensity_scope = [0,1] as number[]
let capacity_scope = [0,1] as number[]


function link_excursion(link_nodes:number[][], multiple_num: number) {
  // 计算路段的偏移值
  const delta_lat = link_nodes[0][0] - link_nodes[1][0]
  const delta_lng = link_nodes[0][1] - link_nodes[1][1]
  let lat_mv = -delta_lng/Math.sqrt(delta_lat*delta_lat+delta_lng*delta_lng)
  let lng_mv = delta_lat/Math.sqrt(delta_lat*delta_lat+delta_lng*delta_lng)
  return [
    [link_nodes[0][0]+lat_mv*multiple_num, link_nodes[0][1]+lng_mv*multiple_num],
    [link_nodes[1][0]+lat_mv*multiple_num, link_nodes[1][1]+lng_mv*multiple_num]
  ]
}

// 计算路段的样式
function link_style(link_idx: number) {
  // 宽度
  let line_weight = Math.pow(1.5, map_zoom_ratio.value-12)*Math.abs(6 + 4*link_flow_ratio[link_idx])
  if (link_flow_ratio[link_idx] == 2 || link_flow_ratio[link_idx] == -2) {
    line_weight = Math.pow(1.5, map_zoom_ratio.value-12)*6
  }
  // 透明度
  let linkOpacity = 0.5
  if (link_clicked.value != -1) {
    if (link_clicked.value == link_idx) {
      linkOpacity = 0.8
    } else linkOpacity = 0.2
  }

  let line_color = "rgba("
  // 颜色
  if (link_speed_ratio[link_idx] > 0) {
    line_color += "" + (255-225*link_speed_ratio[link_idx]) + ",255,30," + linkOpacity + ")"
  } else {
    line_color += "255," + (255+225*link_speed_ratio[link_idx]) + ",30," + linkOpacity + ")"
  }
  if (link_speed_ratio[link_idx] == 2) {
    line_color = "rgba(0, 255, 178," + linkOpacity + ")"
  } else if (link_flow_ratio[link_idx] == -2) {
    line_color = "rgba(195,195,195," + linkOpacity + ")"
  }
  return {
    color: line_color,//线的颜色
    // fillOpacity: 0.5,
    weight: line_weight //线的粗细
  }
}

// 画上节点和线段的外层函数
function draw_links_and_nodes() {
  const circle_radius = Math.pow(1.5,map_zoom_ratio.value-12)
  
  // 转化为lealfet的折线与点
  const max_dot_flow_sum = Math.max(...dots_flow_sum)
  for (let i=0; i<dots_pos.length; i++) {
    const now_circle_radius_mp = dots_flow_sum[i]/max_dot_flow_sum*8+4
    let nodeColor = '#0380df'
    if (node_clicked.value == i) nodeColor = "#bfd8ff"
    dots_in_map.push(new SelectableNode([dots_pos[i][0], dots_pos[i][1]], [dots_a_idx[i], dots_b_idx[i]], i, { 
      // radius: 5, 
      radius: now_circle_radius_mp*circle_radius,
      weight: circle_radius/2+2,
      color: nodeColor,
      fillColor: '#B7B7B7',
      fillOpacity: 1 
    }))
  }

  const line_weight_mp = Math.pow(0.8, map_zoom_ratio.value-12)
  
  for (let i=0; i<links_pos.length; i++) {
    const now_line_weight = line_weight_mp*Math.abs(6 + 4*link_flow_ratio[i])
    const now_link_pos = link_excursion(links_pos[i], now_line_weight*0.00018+0.00002)
    
    links_in_map.push(new SelectablePolyline([[
        now_link_pos[0][0],
        now_link_pos[0][1]
      ], [
        now_link_pos[1][0],
        now_link_pos[1][1]
      ]], [link_a_idx[i], link_b_idx[i]], i, link_style(i)))
  }
  drawLinesAndDots()
}

// 监控选中的网络是否变化
watch(
  () => networkSelData.networks_show,
  (newValue: number[], oldValue: number[]) => {
    dots_pos = new Array<number[]>()
    links_pos = new Array<number[][]>()
    dots_a_idx = new Array<number>()
    dots_b_idx = new Array<number>()
    link_a_idx = new Array<number>()
    link_b_idx = new Array<number>()
    link_flow_ratio = new Array<number>()
    link_speed_ratio = new Array<number>()
    dots_in_links = []
    dots_flow_sum = []
    dots_adjacency_matrix = [] // 邻接矩阵

    // 重新获取网络的数据
    rmFormerLinesAndDots()
    // 判断是否需要展示地图
    if (networkSelData.last_sel_network_id == -1) return
    // if (newValue.length == 1) {
      // const sel_network_data = networkData.getSelNetworkMapInfo(newValue[0])
    if (networkSelData.real_networks_show_max == 1) {
      const sel_network_data = networkData.getSelNetworkMapInfo(networkSelData.last_sel_network_id)
      // 保存fftt范围
      const tmp_scope_res = networkData.getNetworkValScope(networkSelData.last_sel_network_id)
      fftt_dimensity_scope = tmp_scope_res.fftt_dimensity_scope
      capacity_scope = tmp_scope_res.capacity_scope

      // 继续保存节点
      dots_pos = sel_network_data.nodes_pos
      links_pos = sel_network_data.links_pos
      dots_in_links = sel_network_data.nodes_in_links
      for (let i=0; i<dots_pos.length; i++) {
        dots_a_idx.push(i)
        dots_b_idx.push(-1)
      }
      for (let i=0; i<links_pos.length; i++) {
        link_a_idx.push(i)
        link_b_idx.push(-1)
      }
      
      // 获取系数
      flow_scope = sel_network_data.links_flow_scope
      speed_scope = sel_network_data.links_speed_scope
      console.log("speed scope: ", speed_scope);
      for (let i=0; i<sel_network_data.links_flow.length; i++) {
        const now_flow = sel_network_data.links_flow[i]
        const now_speed = sel_network_data.links_speed[i]
        link_flow_ratio.push((now_flow-flow_scope[0])*2/(flow_scope[1]-flow_scope[0])-1)
        link_speed_ratio.push((now_speed-speed_scope[0])*2/(speed_scope[1]-speed_scope[0])-1)
      }
    } else if (newValue.length == 2) {
      const sel_network_data = networkData.getSelComparedNetworksMapInfo(newValue[1], newValue[0])
      dots_pos = sel_network_data.nodes_pos
      links_pos = sel_network_data.links_pos
      dots_in_links = sel_network_data.nodes_in_links // 路段点id

      dots_a_idx = sel_network_data.nodes2a
      dots_b_idx = sel_network_data.nodes2b
      // 路段的id
      link_a_idx = sel_network_data.links2a
      link_b_idx = sel_network_data.links2b
      // 获取系数
      for (let i=0; i<sel_network_data.compared_links_flow.length; i++) {
        const now_flow = sel_network_data.compared_links_flow[i]
        const flow_scope = sel_network_data.delta_flow_scope
        const now_speed = sel_network_data.compared_links_speed[i]
        const speed_scope = sel_network_data.delta_speed_scope
        if (sel_network_data.compared_links_state[i]) {
          link_flow_ratio.push(now_flow/flow_scope)
          link_speed_ratio.push(now_speed/speed_scope)
        } else {
          link_flow_ratio.push(0)
          if (now_speed > 0) link_speed_ratio.push(2)
          else link_speed_ratio.push(-2)
        }
      }
    } else {
      return
    }
    
    // 计算每隔节点的流总数
    dots_flow_sum = new Array<number>(dots_pos.length).fill(0)
    dots_adjacency_matrix = new Array<boolean[]>(dots_pos.length).fill(new Array<boolean>(dots_pos.length).fill(false))
    for (let i=0; i<dots_in_links.length; i++) {
      dots_flow_sum[dots_in_links[i][0]] += link_flow_ratio[i]+1
      dots_flow_sum[dots_in_links[i][1]] += link_flow_ratio[i]+1
      dots_adjacency_matrix[dots_in_links[i][0]][dots_in_links[i][1]] = true
      dots_adjacency_matrix[dots_in_links[i][1]][dots_in_links[i][0]] = true
    }
    draw_links_and_nodes()
  },
  {deep: true}
)

function map_show() {
  if (map != undefined) {
    return false
  }
  
  // 创建地图并设置中心点坐标和缩放级别
  map = L.map('map').setView([43.5528027552607, -96.74700008207309], 12);
  map.setMinZoom(12);
  map.setMaxZoom(15);

  // 添加地图图层
  var tiles = 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png';
  
  var tileLayer = L.tileLayer(tiles, {
      //attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
  }).addTo(map);
  tileLayer.bringToBack();

  // 创建绘图控件
  var drawnItems = new L.FeatureGroup();
  map.addLayer(drawnItems);
  L.control.scale().addTo(map);

  // 地图缩放比例尺
  map.on('zoomend', function () {
    map_zoom_ratio.value = map.getZoom()
    // console.log("map zoom ratio: ", map_zoom_ratio.value);
    // 删除节点
    rmFormerLinesAndDots()
    draw_links_and_nodes()
      // var zoomLevel = map.getZoom();
      // console.log(zoomLevel);  // 输出当前缩放比例
      // const element =
      //     document.querySelector("#map > div.leaflet-control-container > div.leaflet-bottom.leaflet-left > div");
      // document.getElementById("scaler").innerHTML = element.innerHTML
      // _this.set_scaler_color();
  });

  map.on('mousemove', function (e) {
    // console.log(e.latlng)
    
  });
  map.on('click', function(e: L.LeafletMouseEvent) {
    console.log(e.latlng)
  })

  return
}

onMounted(() => {
  map_show()
  // map_show(0);
})

// 地图中的工具栏
const menu_show = ref(-1)
const menu_show_state = ref(0)
const menu_pos = ref([0,0])
const node_clicked = ref(-1)
function handleNodeClick(e: MouseEvent, node_idx: number) {
  // 移除路段的样式
  if (link_clicked.value != -1) {
    link_clicked.value = -1
    // 重设样式
    rmFormerLinesAndDots()
    draw_links_and_nodes()
  }
  
  // 判断菜单栏的方位
  let menu_left = e.clientX+5
  let menu_top = e.clientY

  const map_left = document.getElementById('map')?.offsetLeft as number
  const map_top = document.getElementById('map')?.offsetWidth as number
  if (menu_left + 100 > map_left+map_top) menu_left-=110

  menu_pos.value = [menu_left, e.clientY]
  menu_show_state.value = 0
  menu_show.value = 0

  // 存储点击的节点id
  node_clicked.value = node_idx

  // 给正在编辑的节点添加class
  dots_in_map[node_clicked.value].setStyle({
    color: '#bfd8ff'
  })
  const nodeElement = dots_in_map[node_clicked.value].getElement() as HTMLElement
  nodeElement.classList.add('node_edit')
}
function handleLinkClick(e: MouseEvent, link_idx: number) {
  // 判断是否需要删除之前的路段
  if (now_new_line!=undefined && map.hasLayer(now_new_line)) {
    map.removeLayer(now_new_line)
  }
  // 移除节点的样式
  if (node_clicked.value != -1) {
    dots_in_map[node_clicked.value].setStyle({
      color: '#0380df'
    })
    node_clicked.value = -1
  }

  // 保存需要修改的路段
  link_clicked.value = link_idx

  // 计算菜单栏的位置
  let menu_left = e.clientX+5
  let menu_top = e.clientY

  const map_left = document.getElementById('map')?.offsetLeft as number
  const map_top = document.getElementById('map')?.offsetWidth as number
  if (menu_left + 100 > map_left+map_top) menu_left-=110

  menu_pos.value = [menu_left, e.clientY]
  menu_show_state.value = 0
  menu_show.value = 1

  // 保存路段相关信息
  const network_idx = networkSelData.last_sel_network_id
  lineEditData.lineIdx = link_idx
  lineEditData.newCapacity = networkData.networksInfoArr[network_idx].links[link_idx].capacity
  lineEditData.newFreeFlowTravelTime = networkData.networksInfoArr[network_idx].links[link_idx].freeFlowTravelTime

  // 更改路段的样式
  rmFormerLinesAndDots()
  draw_links_and_nodes()
}
// 创建新线段相关
function handleNewLinkStart() {
  // 设置为编辑模式
  lineEditData.editState = 1
  
  const start_node_idx = node_clicked.value
  // 判断是否需要删除之前的路段
  if (now_new_line!=undefined && map.hasLayer(now_new_line)) {
    map.removeLayer(now_new_line)
  }

  // 新建临时路段
  const now_show_network_idx = networkSelData.last_sel_network_id
  const startNode = networkData.networksInfoArr[now_show_network_idx].nodes[start_node_idx]
  lineEditData.networkIdx = now_show_network_idx
  lineEditData.startNodeIdx = start_node_idx
  lineEditData.startNodePos = [startNode.lat, startNode.lon]
  now_new_line = L.polyline([[lineEditData.startNodePos[0], lineEditData.startNodePos[1]]], {
    // color: '#1FD86D55',//线的颜色
    color: '#fff',
    // fillOpacity: 0.5,
    weight: 6, //线的粗细
    dashArray: "5, 20"
  }).addTo(map)
  now_new_line.bringToBack()

  // 开始鼠标跟随
  map.on('mousemove', onMouseMove)

  // 设置菜单栏显示取消和保存
  menu_show_state.value = 1
}
function handleCancelNewLink() {
  menu_show_state.value = 0
  // 判断是否需要删除之前的路段
  if (now_new_line!=undefined && map.hasLayer(now_new_line)) {
    map.removeLayer(now_new_line)
  }
  lineEditData.editState = 0
  menu_show.value = 0
  map.off('mousemove', onMouseMove)
}
// 创建新线段的触摸控制
const new_link_info_width = computed(() => {
  // 判断是否非法
  const network_idx = networkSelData.last_sel_network_id
  if (lineEditData.startNodeIdx<0 || lineEditData.endNodeIdx<0 || node_clicked.value==-1) {
    return {
      fftt_width: 0,
      i_fftt_width: 0,
      cap_width: 0,
      i_cap_width: 0
    }
  }

  // 计算fftt
  const Node1 = networkData.networksInfoArr[network_idx].nodes[lineEditData.startNodeIdx]
  const Node2 = networkData.networksInfoArr[network_idx].nodes[lineEditData.endNodeIdx]
  const pos_dis = Math.sqrt(Math.pow(Node1.lat-Node2.lat, 2) + Math.pow(Node1.lon-Node2.lon, 2))
  const now_fftt_dimensity = lineEditData.newFreeFlowTravelTime/pos_dis
  const now_i_fftt_dimensity = lineEditData.newIFreeFlowTravelTime/pos_dis
  const now_fftt_width = (now_fftt_dimensity-fftt_dimensity_scope[0])/(fftt_dimensity_scope[1]-fftt_dimensity_scope[0])*80
  const now_i_fftt_width = (now_i_fftt_dimensity-fftt_dimensity_scope[0])/(fftt_dimensity_scope[1]-fftt_dimensity_scope[0])*80

  // 计算capacity
  const now_capacity_width = (lineEditData.newCapacity-capacity_scope[0])/(capacity_scope[1]-capacity_scope[0])*80
  const now_i_capacity_width = (lineEditData.newICapacity-capacity_scope[0])/(capacity_scope[1]-capacity_scope[0])*80
  // console.log("now fftt",link_clicked.value,": ", now_fftt_dimensity);
  return {
    fftt_width: now_fftt_width,
    i_fftt_width: now_i_fftt_width,
    cap_width: now_capacity_width,
    i_cap_width: now_i_capacity_width
  }
})
function handleNewLinkFFTTPush(e: MouseEvent, link_type: number) {
  if (e.buttons == 1) {
    // 鼠标的左键按下
    // 计算路段的长度
    const network_idx = networkSelData.last_sel_network_id
    const Node1 = networkData.networksInfoArr[network_idx].nodes[lineEditData.startNodeIdx]
    const Node2 = networkData.networksInfoArr[network_idx].nodes[lineEditData.endNodeIdx]
    const pos_dis = Math.sqrt(Math.pow(Node1.lat-Node2.lat, 2) + Math.pow(Node1.lon-Node2.lon, 2))
    
    // 推算出ttff
    const ttff_val = e.offsetX /80
    let new_ttff = ttff_val*(fftt_dimensity_scope[1]-fftt_dimensity_scope[0])+fftt_dimensity_scope[0]
    new_ttff *= pos_dis
    
    if (link_type == 0) {
      lineEditData.newFreeFlowTravelTime = new_ttff
    } else {
      lineEditData.newIFreeFlowTravelTime = new_ttff
    }
  }
}
function handleNewLinkCapacityPush(e: MouseEvent, link_type: number) {
  if (e.buttons == 1) {
    // 鼠标的左键按下
    // 推算出capacity
    const cap_val = e.offsetX /80
    const new_capacity = cap_val*(capacity_scope[1]-capacity_scope[0])+capacity_scope[0]
    if (link_type == 0) {
      lineEditData.newCapacity = new_capacity
    } else {
      lineEditData.newICapacity = new_capacity
    }
  }
}
// 保存新建的道路
function saveNewLink1(e: MouseEvent) {
  menu_show_state.value = 0
  let menu_left = e.clientX+5
  let menu_top = e.clientY

  const map_left = document.getElementById('map')?.offsetLeft as number
  const map_top = document.getElementById('map')?.offsetWidth as number
  if (menu_left + 230 > map_left+map_top) menu_left-=220

  menu_pos.value = [menu_left, e.clientY]
  menu_show_state.value = 0
  menu_show.value = 2
}
async function save_new_road() {
  menu_show.value = -1
  menu_show_state.value = 0
  node_clicked.value = -1
  // 判断是否需要删除之前的路段
  if (now_new_line!=undefined && map.hasLayer(now_new_line)) {
    map.removeLayer(now_new_line)
  }

  // 判断当前是否可以保存路段的新增
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
function switchNewWayNum() {
  lineEditData.isBidirection = !lineEditData.isBidirection
}
const switch_way_num_btn = computed(() => {
  let icon_src = "/static/edits_btn/one_way.svg"
  if (lineEditData.isBidirection) icon_src = "/static/edits_btn/two_way.svg"
  return icon_src
})

// 修改路段相关的
function show_menu_from_idx(reset_info_type: number) {
  menu_show.value = reset_info_type
  menu_show_state.value = 0
  const link_idx = link_clicked.value

  if (menu_show.value == 1 && link_idx>=0) {
    // 重新加入路段信息
    const network_idx = networkSelData.last_sel_network_id
    lineEditData.newCapacity = networkData.networksInfoArr[network_idx].links[link_idx].capacity
    lineEditData.newFreeFlowTravelTime = networkData.networksInfoArr[network_idx].links[link_idx].freeFlowTravelTime
  }
}
// 点击修改路段的free flow travel time
const fftt_set_width = computed(() => {
  // console.log("fftt scope: ", fftt_dimensity_scope);
  
  const network_idx = networkSelData.last_sel_network_id
  if (network_idx<0 || link_clicked.value==-1) return 0
  const now_link = networkData.networksInfoArr[network_idx].links[link_clicked.value]
  const Node1 = networkData.networksInfoArr[network_idx].nodes[now_link.pInNode]
  const Node2 = networkData.networksInfoArr[network_idx].nodes[now_link.pOutNode]
  const pos_dis = Math.sqrt(Math.pow(Node1.lat-Node2.lat, 2) + Math.pow(Node1.lon-Node2.lon, 2))
  const now_fftt_dimensity = lineEditData.newFreeFlowTravelTime/pos_dis
  // console.log("now fftt",link_clicked.value,": ", now_fftt_dimensity);
  
  return (now_fftt_dimensity-fftt_dimensity_scope[0])/(fftt_dimensity_scope[1]-fftt_dimensity_scope[0])*83
})
function handleFFTTReset(e: MouseEvent) {
  if (e.buttons == 1) {
    // 鼠标的左键按下
    // 计算路段的长度
    const network_idx = networkSelData.last_sel_network_id
    const now_link = networkData.networksInfoArr[network_idx].links[link_clicked.value]
    const Node1 = networkData.networksInfoArr[network_idx].nodes[now_link.pInNode]
    const Node2 = networkData.networksInfoArr[network_idx].nodes[now_link.pOutNode]
    const pos_dis = Math.sqrt(Math.pow(Node1.lat-Node2.lat, 2) + Math.pow(Node1.lon-Node2.lon, 2))
    
    // 推算出ttff
    const ttff_val = e.offsetX /83
    let new_ttff = ttff_val*(fftt_dimensity_scope[1]-fftt_dimensity_scope[0])+fftt_dimensity_scope[0]
    new_ttff *= pos_dis
    lineEditData.newFreeFlowTravelTime = new_ttff
  }
}
// 点击修改路段的capacity
const capacity_set_width = computed(() => {
  const network_idx = networkSelData.last_sel_network_id
  if (network_idx<0 || link_clicked.value==-1) return 0
  return (lineEditData.newCapacity-capacity_scope[0])/(capacity_scope[1]-capacity_scope[0])*83
})
function handleCapacityReset(e: MouseEvent) {
  if (e.buttons == 1) {
    // 鼠标的左键按下
    // 推算出capacity
    console.log("capacity_scope ", capacity_scope);
    
    const cap_val = e.offsetX /83
    const new_capacity = cap_val*(capacity_scope[1]-capacity_scope[0])+capacity_scope[0]
    lineEditData.newCapacity = new_capacity
  }
}

// 新建节点相关
watch(
  () => lineEditData.newNodePos,
  (newValue: number) => {
    // 计算节点的位置
    const network_idx = networkSelData.last_sel_network_id
    const now_link = networkData.networksInfoArr[network_idx].links[link_clicked.value]
    const Node1 = networkData.networksInfoArr[network_idx].nodes[now_link.pInNode]
    const Node2 = networkData.networksInfoArr[network_idx].nodes[now_link.pOutNode]
    lineEditData.newNodeLat = Node1.lat*(1-lineEditData.newNodePos) + Node2.lat*lineEditData.newNodePos
    lineEditData.newNodeLng = Node1.lon*(1-lineEditData.newNodePos) + Node2.lon*lineEditData.newNodePos
  }
)
// function (params:type) {
  
// }

// 监听文档点击事件
document.addEventListener('click', function(event) {
  const map_area_content = document.getElementById('map_area') as HTMLElement
  // 判断点击的目标元素是否是对话框内的元素
  const isClickInsideNodeMenu = map_area_content.contains(event.target as HTMLElement)

  // 如果点击的目标元素不是对话框内的元素，则关闭对话框
  if (!isClickInsideNodeMenu && menu_show.value != -1) {
    // 关闭对话框的代码
    menu_show.value = -1
    menu_show_state.value = 0

    // 移除节点的样式
    if (node_clicked.value != -1) {
      dots_in_map[node_clicked.value].setStyle({
        color: '#0380df'
      })
      node_clicked.value = -1
    }

    // 移除路段的样式
    if (link_clicked.value != -1) {
      link_clicked.value = -1
      // 重设样式
      rmFormerLinesAndDots()
      draw_links_and_nodes()
    }
  }
});

</script>
<template>
  <div class="main_board" id="map_area">
    <div class="map_block">
      <div id="map"></div>
    </div>
    <div id="node_menu" :class="{not_show_container: menu_show!=0}"
      :style="{left:menu_pos[0]+'px', top: menu_pos[1]+'px'}">
      <div class="state_box" :class="{not_show_container: menu_show_state!=0}">
        <div class="edit_btn" title="Add a link start from the node"
          @click="handleNewLinkStart()">
          <img src="/static/edits_btn/add_link.svg" alt="" srcset="">
        </div>
        <div class="edit_btn" title="Delete this node">
          <img src="/static/edits_btn/del_pt.svg" alt="" srcset="">
        </div>
      </div>
      <div class="state_box" :class="{not_show_container: menu_show_state!=1}">
        <div class="edit_btn" title="Cancel"
          @click="handleCancelNewLink()">
          <img src="/static/edits_btn/cancel.svg" alt="" srcset="">
        </div>
        <div class="edit_btn" title="Save"
          @click="saveNewLink1($event)">
          <img src="/static/edits_btn/save.svg" alt="" srcset="">
        </div>
      </div>
    </div>
    <div id="link_menu" :class="{not_show_container: menu_show!=1, state1: menu_show_state==0}"
      :style="{left:menu_pos[0]+'px', top: menu_pos[1]+'px'}">
      <div class="state_box" :class="{not_show_container: menu_show_state!=0}">
        <div class="edit_btn" title="Change road free flow travel time"
          @click="show_menu_from_idx(3)">
          <img src="/static/edits_btn/speed_edit.svg" alt="" srcset="">
        </div>
        <div class="edit_btn" title="Change road capacity"
          @click="show_menu_from_idx(4)">
          <img src="/static/edits_btn/capacity_edit.svg" alt="" srcset="">
        </div>
        <div class="edit_btn" title="Delete this road">
          <img src="/static/edits_btn/del_link.svg" alt="" srcset="">
        </div>
        <div class="edit_btn" title="Add a node on this road">
          <img src="/static/edits_btn/add_pt.svg" alt="" srcset="">
        </div>
      </div>
      <div class="state_box" :class="{not_show_container: menu_show_state!=1}">
        <div class="edit_btn" title="Cancel">
          <img src="/static/edits_btn/cancel.svg" alt="" srcset="">
        </div>
        <div class="edit_btn" title="Save">
          <img src="/static/edits_btn/save.svg" alt="" srcset="">
        </div>
      </div>
    </div>
    <div id="new_link_menu" :class="{not_show_container: menu_show!=2}"
        :style="{left:menu_pos[0]+'px', top: menu_pos[1]+'px'}">
      <div class="menu_content">
        <div class="col_btn_box">
            <div class="edit_btn" title="Cancel"
              @click="handleCancelNewLink()">
                <img src="/static/edits_btn/cancel.svg" alt="" srcset="">
            </div>
            <div class="edit_btn" title="Save"
              @click="save_new_road()">
                <img src="/static/edits_btn/save.svg" alt="" srcset="">
            </div>
            <div class="edit_btn" title="Switching between two-way roads and one-way roads"
              @click="switchNewWayNum()">
                <img :src="switch_way_num_btn" alt="" srcset="">
            </div>
        </div>
        <div class="menu_input_part">
            <div class="input_pair">
                <div class="input_title">
                    free flow travel time
                </div>
                <div class="input_box">
                    <div class="val_input_box">
                        <input type="number" min="0" v-model="lineEditData.newFreeFlowTravelTime">
                    </div>
                    <div class="range_input_box fftt_ipt"
                      @mousemove="handleNewLinkFFTTPush($event, 0)"
                      @mousedown="handleNewLinkFFTTPush($event, 0)">
                        <div class="range_input_content"
                          :style="{width: new_link_info_width.fftt_width + 'px'}"></div>
                    </div>
                </div>
            </div>
            <div class="input_pair">
                <div class="input_title">
                    capacity
                </div>
                <div class="input_box">
                    <div class="val_input_box">
                        <input type="number" min="0" v-model="lineEditData.newCapacity">
                    </div>
                    <div class="range_input_box capacity_ipt"
                      @mousemove="handleNewLinkCapacityPush($event, 0)"
                      @mousedown="handleNewLinkCapacityPush($event, 0)">
                        <div class="range_input_content"
                          :style="{width: new_link_info_width.cap_width + 'px'}"></div>
                    </div>
                </div>
            </div>
            <div class="input_pair" :class="{not_show_container: !lineEditData.isBidirection}">
                <div class="input_title">
                    opposite free flow travel time
                </div>
                <div class="input_box">
                    <div class="val_input_box">
                        <input type="number" min="0" v-model="lineEditData.newIFreeFlowTravelTime">
                    </div>
                    <div class="range_input_box fftt_ipt"
                      @mousemove="handleNewLinkFFTTPush($event, 1)"
                      @mousedown="handleNewLinkFFTTPush($event, 1)">
                        <div class="range_input_content"
                          :style="{width: new_link_info_width.i_fftt_width + 'px'}"></div>
                    </div>
                </div>
            </div>
            <div class="input_pair" :class="{not_show_container: !lineEditData.isBidirection}">
                <div class="input_title">
                    opposite capacity
                </div>
                <div class="input_box">
                    <div class="val_input_box">
                        <input type="number" min="0" v-model="lineEditData.newICapacity">
                    </div>
                    <div class="range_input_box capacity_ipt"
                      @mousemove="handleNewLinkCapacityPush($event, 1)"
                      @mousedown="handleNewLinkCapacityPush($event, 1)">
                        <div class="range_input_content"
                          :style="{width: new_link_info_width.i_cap_width + 'px'}"></div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
    <div id="edit_link_speed_menu" class="edit_link_menu" :class="{not_show_container: menu_show!=3}"
      :style="{left:menu_pos[0]+'px', top: menu_pos[1]+'px'}">
      <div class="menu_content">
          <div class="col_btn_box">
              <div class="edit_btn" title="Cancel"
                @click="show_menu_from_idx(1)">
                  <img src="/static/edits_btn/cancel.svg" alt="" srcset="">
              </div>
              <div class="edit_btn" title="Save">
                  <img src="static/edits_btn/save.svg" alt="" srcset="">
              </div>
          </div>
          <div class="menu_input_part">
              <div class="input_pair">
                  <div class="input_title">
                      Free Flow Travel Time
                  </div>
                  <div class="input_box">
                      <div class="val_input_box">
                          <input type="number" v-model="lineEditData.newFreeFlowTravelTime">
                      </div>
                      <div class="range_input_box fftt_ipt"
                        @mousedown="handleFFTTReset($event)"
                        @mousemove="handleFFTTReset($event)">
                          <div class="range_input_content"
                            :style="{width: fftt_set_width+'px'}"></div>
                      </div>
                  </div>
              </div>
          </div>
      </div>
    </div>
    <div id="edit_link_capacity_menu" class="edit_link_menu" :class="{not_show_container: menu_show!=4}"
      :style="{left:menu_pos[0]+'px', top: menu_pos[1]+'px'}">
      <div class="menu_content">
          <div class="col_btn_box">
              <div class="edit_btn" title="Cancel"
                @click="show_menu_from_idx(1)">
                  <img src="/static/edits_btn/cancel.svg" alt="" srcset="">
              </div>
              <div class="edit_btn" title="Save">
                  <img src="/static/edits_btn/save.svg" alt="" srcset="">
              </div>
          </div>
          <div class="menu_input_part">
              <div class="input_pair">
                  <div class="input_title">
                      Capacity
                  </div>
                  <div class="input_box">
                      <div class="val_input_box">
                          <input type="number" v-model="lineEditData.newCapacity">
                      </div>
                      <div class="range_input_box fftt_ipt"
                        @mousedown="handleCapacityReset($event)"
                        @mousemove="handleCapacityReset($event)">
                          <div class="range_input_content"
                            :style="{width: capacity_set_width+'px'}"></div>
                      </div>
                  </div>
              </div>
          </div>
      </div>
    </div>
    <div id="new_node_menu" :class="{not_show_container: menu_show!=5}"
      :style="{left:menu_pos[0]+'px', top: menu_pos[1]+'px'}">
      <div class="menu_content">
        <div class="col_btn_box">
            <div class="edit_btn" title="Cancel">
                <img src="/static/edits_btn/cancel.svg" alt="" srcset="">
            </div>
            <div class="edit_btn" title="Save">
                <img src="/static/edits_btn/save.svg" alt="" srcset="">
            </div>
        </div>
        <div class="menu_input_part menu_nodepos_input_part">
            <div class="input_pair">
                <div class="input_title">
                    Node Position
                </div>
                <div class="input_box">
                    <div class="val_input_box nodepos_range_box" >
                        <input type="range" min="0" max="1" v-model="lineEditData.newNodePos">
                    </div>
                    <div class="val_input_box nodepos_input_pair_box">
                        <div class="nodepos_input_pair">
                            <div class="nodepos_input_title_box">
                                Lat
                            </div>
                            <div class="nodepos_input_box">
                                <input type="number" v-model="lineEditData.newNodeLat">
                            </div>
                        </div>
                        <div class="nodepos_input_pair">
                            <div class="nodepos_input_title_box">
                                Lng
                            </div>
                            <div class="nodepos_input_box">
                                <input type="number" v-model="lineEditData.newNodeLng">
                            </div>
                        </div>
                    </div>
                    <!-- <div class="range_input_box fftt_ipt">
                        <div class="range_input_content"></div>
                    </div> -->
                </div>
            </div>
        </div>
        <div class="menu_input_part">
            <div class="input_pair">
                <div class="input_title">
                    Road1 Free Flow Travel Time
                </div>
                <div class="input_box">
                    <div class="val_input_box">
                        <input type="number">
                    </div>
                    <div class="range_input_box fftt_ipt">
                        <div class="range_input_content"></div>
                    </div>
                </div>
            </div>
        </div>
        <div class="menu_input_part">
            <div class="input_pair">
                <div class="input_title">
                    Road2 Free Flow Travel Time
                </div>
                <div class="input_box">
                    <div class="val_input_box">
                        <input type="number">
                    </div>
                    <div class="range_input_box fftt_ipt">
                        <div class="range_input_content"></div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://unpkg.com/leaflet@1.7.1/dist/leaflet.css');
@import url('https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css');
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

.main_board .map_block {
  margin-left: auto;
  margin-right: auto;
  width: calc(100% - 18px);
  height: calc(100% - 18px);
  border-radius: 3px;

  background-color: aliceblue;
  overflow: hidden;
}

.map_block #map {
  width: 100%;
  height: 100%;
  z-index: 0;
}

.not_show_container {
  display: none;
}

/* 菜单栏目 */
#node_menu, #link_menu {
  z-index: 2;
  position: absolute;
  width: 100px;
  height: 50px;
  border-radius: 5px;
  background-color: #232323ee;
  box-shadow: 0 0 2px #aaa;
}
#link_menu.state1 {
  height: 100px;
}
.edit_btn {
  display: inline-block;
  width: 30px;
  height: 30px;
  padding: 5px;
  border-radius: 3px;
  margin: 5px;
  background-color: #33333399;
}
.edit_btn:hover {
  background-color: #565656;
  cursor: pointer;
}
.edit_btn img {
  height: 30px;
  width: 30px;
}

</style>