<script setup lang="ts">
import L, { polyline } from 'leaflet';
import 'leaflet-draw';
import { useNetworksData } from '@/stores/networkData';
import { useNetworkSel } from '@/stores/networkSel';
import { useLineEdit } from '@/stores/lineEdit';
import { onMounted, ref } from 'vue';
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
    // 添加点击事件监听器
    this.on('click', (e: L.LeafletMouseEvent) => {
      this.isSelected = !this.isSelected;
      const nodes_in_link = this.getLatLngs()
      // const link_len = Math.sqrt(Math.pow(nodes_in_link[0][0],2))
      console.log("link len: ", e.target);
      
      // const now_show_network_idx = networkSelData.last_sel_network_id
      // if (now_show_network_idx == -1) return
      // console.log("link len: ", networkData.networksInfoArr[now_show_network_idx].links[former_idxs[0]].freeFlowTravelTime);
      
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

    // Add click event listener
    this.on('click', () => {
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
  let line_color = "rgba("
  // 颜色
  if (link_speed_ratio[link_idx] > 0) {
    line_color += "255," + (255-225*link_speed_ratio[link_idx]) + ",30,0.5)"
  } else {
    line_color += "" + (255+225*link_speed_ratio[link_idx]) + ",255,30,0.5)"
  }
  if (link_speed_ratio[link_idx] == 2) {
    line_color = "#00FFB288"
  } else if (link_flow_ratio[link_idx] == -2) {
    line_color = "rgba(195,195,195,0.5)"
  }
  return {
    color: line_color,//线的颜色
    fillOpacity: 0.5,
    weight: line_weight //线的粗细
  }
}

// 画上节点和线段的外层函数
function draw_links_and_nodes() {
  const circle_radius = Math.pow(1.8,map_zoom_ratio.value-12)
  
  // 转化为lealfet的折线与点
  const max_dot_flow_sum = Math.max(...dots_flow_sum)
  for (let i=0; i<dots_pos.length; i++) {
    const now_circle_radius_mp = dots_flow_sum[i]/max_dot_flow_sum*4+4
    dots_in_map.push(new SelectableNode([dots_pos[i][0], dots_pos[i][1]], [dots_a_idx[i], dots_b_idx[i]], i, { 
      // radius: 5, 
      radius: now_circle_radius_mp*circle_radius,
      weight: circle_radius/2+2,
      color: '#0070C1',
      fillColor: '#fff',
      fillOpacity: 1 
    }))
  }

  const line_weight_mp = Math.pow(0.8, map_zoom_ratio.value-12)
  console.log(links_pos.length);
  
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
    if (newValue.length == 1) {
      const sel_network_data = networkData.getSelNetworkMapInfo(newValue[0])
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
      for (let i=0; i<sel_network_data.links_flow.length; i++) {
        const now_flow = sel_network_data.links_flow[i]
        const flow_scope = sel_network_data.links_flow_scope
        const now_speed = sel_network_data.links_speed[i]
        const speed_scope = sel_network_data.links_speed_scope
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
  // console.log("map: ", map);
  if (map != undefined) {
    return false
  }
  
  // 创建地图并设置中心点坐标和缩放级别
  map = L.map('map').setView([43.5528027552607, -96.74700008207309], 12);
  map.setMinZoom(12);
  map.setMaxZoom(15);

  // 添加地图图层
  var tiles = 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png';
  
  var tileLayer = L.tileLayer(tiles, {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
      // attribution_control: true,
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

  // 添加绘图控件
  // var drawControl = new L.Control.Draw({
  //     edit: {
  //         featureGroup: drawnItems
  //     }
  // });
  // map.addControl(drawControl);

  // let paint_select_map = this.paint_select_map;
  // let paint_area_relation = this.paint_area_relation;
  // let _this = this;

  // // 地图缩放比例尺
  // map.on('zoomend', function () {
  //     // var zoomLevel = map.getZoom();
  //     // console.log(zoomLevel);  // 输出当前缩放比例
  //     const element =
  //         document.querySelector("#map > div.leaflet-control-container > div.leaflet-bottom.leaflet-left > div");
  //     document.getElementById("scaler").innerHTML = element.innerHTML
  //     _this.set_scaler_color();
  // });

  // // 监听绘图事件
  // map.on('draw:created', function (e) {
  //     var layer = e.layer;

  //     if (layer instanceof L.Rectangle) { // 确保绘制的是矩形对象
  //         var bounds = layer.getBounds(); // 获取矩形的边界

  //         var startPoint = bounds.getSouthWest(); // 获取矩形的西南角坐标
  //         var endPoint = bounds.getNorthEast(); // 获取矩形的东北角坐标

  //         console.log('Start Point:', startPoint);
  //         console.log('End Point:', endPoint);

  //         let ptA = [startPoint.lat, startPoint.lng]
  //         let ptB = [endPoint.lat, endPoint.lng]
  //         console.log(ptB);

          
  //         document.getElementById('diagramLoading').style.display = "block";
  //         document.getElementById('loadingLayer').style.display = "block";
  //         paint_area_relation(ptA, ptB, 0);
  //         paint_select_map(ptA, ptB, 0, map);
  //     } else {
  //         console.log(layer);
  //         var center = layer.getLatLng();
  //         var radius = layer.getRadius();
  //         let ptA = [center.lat, center.lng];

          
  //         document.getElementById('diagramLoading').style.display = "block";
  //         document.getElementById('loadingLayer').style.display = "block";
  //         paint_area_relation(ptA, radius, 1);
  //         paint_select_map(ptA, radius, 1, map);

  //         console.log('圆心坐标:', center);
  //         console.log('半径:', radius);
  //     }

  //     drawnItems.addLayer(layer);
  // });

  // document.getElementById("clearBtn").onclick = () => {
  //     // 清除所有绘制的图层
  //     map.eachLayer(function (layer) {
  //         if (layer instanceof L.Path || layer instanceof L.Marker) {
  //             map.removeLayer(layer);
  //         }
  //     });
  // }

}

onMounted(() => {
  map_show()
  // map_show(0);
})

</script>
<template>
  <div class="main_window">
    <h2 class="box_title">
      Road Network
    </h2>
    <div class="map_box">
      <div id="map">
        
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://unpkg.com/leaflet@1.7.1/dist/leaflet.css');
@import url('https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css');
.main_window {
  width: 100%;
  height: 100%;
  /* overflow: auto; */
}

.map_box {
  margin: 10px;
  width: calc(100% - 20px);
  height: calc(100% - 52px);
  margin-top: 0;
  background-color: aliceblue;
  border-radius: 5px;
  overflow: hidden;
}

.map_box #map {
  width: 100%;
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
