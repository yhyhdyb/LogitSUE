import { defineStore } from 'pinia'
import axios from 'axios'
import L, { polyline } from 'leaflet';
import 'leaflet-draw';

export const useLineEdit = defineStore('lineEdit', {
  state: () => ({
    editState: 0,
    lineIdx: -1,
    startNodeIdx: -1,
    endNodeIdx: -1,
    networkIdx: -1,
    startNodePos: [] as number[],
    moveEndPos: [] as number[],
    newCapacity: 5000,
    newFreeFlowTravelTime: 5,
    newICapacity: 5000,
    newIFreeFlowTravelTime: 5,
    newNodePos: 0, // 新建的节点在原始线段的相对位置
    newNodeLat: 0, // 新建节点的纬度
    newNodeLng: 0, // 新建节点的经度
    isBidirection: false
  }),
  getters: {
    // 计算属性
  },
  actions: {
    startDraw() {
      if (this.editState == 0) this.editState = 1
      else this.editState = 0
      this.lineIdx = -1
      this.networkIdx = -1
      this.startNodeIdx = -1
      this.startNodePos = []
      this.endNodeIdx = -1
      this.newCapacity = 5000
      this.newFreeFlowTravelTime = 5
      this.newICapacity = 5000
      this.newIFreeFlowTravelTime = 5
    },
    endDraw() {
      this.editState = 0
      this.lineIdx = -1
      this.networkIdx = -1
      this.startNodeIdx = -1
      this.startNodePos = []
      this.endNodeIdx = -1
      this.newCapacity = 5000
      this.newFreeFlowTravelTime = 5
      this.newICapacity = 5000
      this.newIFreeFlowTravelTime = 5
    }
  }
})
