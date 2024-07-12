<script setup lang="ts">
import L from 'leaflet';
import 'leaflet-draw';
import { useNetworksData } from '@/stores/networkData';
import { useNetworkSel } from '@/stores/networkSel';
import { useLineEdit } from '@/stores/lineEdit';
import {onMounted, ref } from 'vue';
import { watch } from 'vue';

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
  }
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

function map_show(map_idx: number) {
  if (map != undefined) {
    return false
  }
  
  // 创建地图并设置中心点坐标和缩放级别
  map = L.map('map'+map_idx,{
  zoomControl: false, // 禁用缩放控件
  dragging: false, // 禁用拖动
  touchZoom: false, // 禁用触摸缩放
  doubleClickZoom: false, // 禁用双击缩放
  scrollWheelZoom: false, // 禁用滚轮缩放
}).setView([43.5528027552607, -96.74700008207309], 12);
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
  return
}

//父组件传入子组件map_id
const props = defineProps({
  map_idx: {
    type: Number,
    default: 0
  }
})

onMounted(() => {
  map_show(props.map_idx)
  // map_show(0);
})

// 地图中的工具栏
const node_clicked = ref(-1)




</script>
<template>
    <div class="map_box">
        <div id="map"></div>
    </div>
</template>

<style scoped>
@import url('https://unpkg.com/leaflet@1.7.1/dist/leaflet.css');
@import url('https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css');

.map_box{
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  height: 100%;
  border-radius: 3px;
  background-color: aliceblue;
  overflow: hidden;
}

.map_box #map {
  width: 100%;
  height: 100%;
}

</style>