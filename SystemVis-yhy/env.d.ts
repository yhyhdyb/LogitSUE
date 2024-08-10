/// <reference types="vite/client" />
interface MyComponent {
  name: string
  initPoint: [number, number]//存储重复点击的那个点
  // isSelected: boolean[]
  shape: [number, number][]
  nSensor: number
  sensors: string[][]
  sensorPositions: [number, number][]
  graphicalFeature: GraphicalFeature
  d: number,
  nArray: number,
  drew: boolean,

  // 以下是画圆的属性
  isCircle: boolean // 是否是圆
  center: [number, number]
  radius: number
}

interface GraphicalFeature {
  leftTopX: number
  leftTopY: number
  componentWidth: number
  componentHeight: number
}
