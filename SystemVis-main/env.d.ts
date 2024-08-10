/// <reference types="vite/client" />
interface MyComponent {
  name: string
  initPoint: [number, number]//存储重复点击的那个点
  // isSelected: boolean[]
  shapeRefined: [number, number][] | ShapeForCircle
  shape: [number, number][] | ShapeForCircle
  nSensor: number
  // sensors: string[][]
  sensorPositions: [number, number, number][]
  sensorValidPositions: [number, number, number][]
  graphicalFeature: GraphicalFeature
  d: number
  nArray: number
  arrayPrefix: string[]
  drew: boolean
  shapeType: string
  mapping: { [pid: number]: string } // pid 第几个position  string->传感器名字
  sensorGroups: SensorGroup[]
  arrayMatchingResults?: [number, number][]
  links: [number, number][]
  hullPaths: string[],
  validSensors: string[]
}

interface RelationsGroup {
  weight: number
  aspect: string
  relations: [number, number][]
}

interface SensorGroup {
  aspect: string,
  groups: string[][]
}

interface GraphicalFeature {
  leftTopX: number
  leftTopY: number
  componentWidth: number
  componentHeight: number
}

interface ShapeForCircle {
  r: number,
  cx: number,
  cy: number
}


interface TypeSimilarity {
  category: { [sid: number]: boolean },
  numeric: { [sid: number]: boolean },
  boolean: { [sid: number]: boolean }
}

interface PositionInfo {
  y: number,
  x: number,
  pid: number
}

type Point = [number, number]
interface VectorPoint {
  p: Point,
  v: Point
}