import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { sensorData } from '@/interface/coal/sensorData'
import { obtainIdealPoints, obtainIdealPointsForCircle } from '../utils/generateGrids'
import { minBy, maxBy, cloneDeep, flatten } from 'lodash'
import { batterySensorNames, batteryStructure, batteryGroupsByType } from '../data/battery'
import { coalSensorNames, coalStructure, coalGroupsByType } from '../data/coal'
import { fetchLayoutGreedy, getLinks, getCommmunityPaths } from '../utils/fetchLayout'
import { orderingPoints } from '@/utils/orderingPoints'
import { processArrayComponent } from '@/utils/processArrayComponent'


export const useStructureStore = defineStore('structure', () => {
  const isMonitoring = ref(false)
  const backgroundImageUrl = ref('')
  // const weights = ref({
  //   location: 1,
  //   measurement: 0.3,
  //   type: 0.5
  // } as { [aspect: string]: number })
  // const sensorNames = ref(batterySensorNames)
  // const structure = ref(batteryStructure)
  // const groupsByType = ref(batteryGroupsByType)

  const weights = ref({
    location: 2,
    measurement: 0,
    type: 0
  } as { [aspect: string]: number })
  const sensorNames = ref(coalSensorNames)
  const structure = ref(coalStructure)
  const groupsByType = ref(coalGroupsByType)

  const flattenStructures = computed(() => {
    let flattenOnes = [] as MyComponent[]
    for (const component of structure.value) {
      const initialLeftTopX = cloneDeep(component.graphicalFeature.leftTopX)
      const initialLeftTopY = cloneDeep(component.graphicalFeature.leftTopY)
      const arrayMatchingResults = component.arrayMatchingResults as [number, number][]
      if (!arrayMatchingResults && component.nArray > 1) {
        continue
      } else if (component.nArray === 1) {
        flattenOnes = flattenOnes.concat(component)
      } else {
        const componentArray = new Array(component.nArray).fill(0).map((_, i) => {
          const c = cloneDeep(component)
          c.name = component.arrayPrefix[i] + component.name
          for (const pid in c.mapping) {
            c.mapping[pid] = component.arrayPrefix[i] + c.mapping[pid]
          }

          if (c.shapeType === 'polygon') {
            for (const p of c.shape as [number, number][]) {
              p[0] += i > 0 ? (arrayMatchingResults[i - 1][0] - initialLeftTopX) : 0
              p[1] += i > 0 ? (arrayMatchingResults[i - 1][1] - initialLeftTopY) : 0
            }
          } else if (c.shapeType === 'circle') {
            ; (c.shape as ShapeForCircle).cx += i > 0 ? (arrayMatchingResults[i - 1][0] - initialLeftTopX) : 0
              ; (c.shape as ShapeForCircle).cy += i > 0 ? (arrayMatchingResults[i - 1][1] - initialLeftTopY) : 0
          }
          // for (const p of c.sensorPositions) {
          //   p[0] += i > 0 ? (arrayMatchingResults[i - 1] - initialLeftTopX)
          //   p[1] += i > 0 ? (arrayMatchingResults[i - 1] - initialLeftTopX)
          // }
          c.graphicalFeature.leftTopX += i > 0 ? (arrayMatchingResults[i - 1][0] - initialLeftTopX) : 0
          c.graphicalFeature.leftTopY += i > 0 ? (arrayMatchingResults[i - 1][1] - initialLeftTopY) : 0
          return c
        }) as MyComponent[]
        console.log(componentArray)
        flattenOnes = flattenOnes.concat(componentArray)
      }

    }
    return flattenOnes
  })

  const setShape = (shape: [number, number][] | ShapeForCircle, name: string, type: string) => {
    structure.value.forEach(async (component) => {
      if (component.name === name) {
        component.shapeType = type
        component.drew = true
        component.shape = shape

        if (type === 'circle') {
          const shapeCircle = shape as ShapeForCircle
          const leftTopX = shapeCircle.cx - shapeCircle.r
          const leftTopY = shapeCircle.cy - shapeCircle.r
          const componentWidth = 2 * shapeCircle.r
          const componentHeight = 2 * shapeCircle.r
          const shapeRefined = {
            cx: shapeCircle.cx - leftTopX,
            cy: shapeCircle.cy - leftTopY,
            r: shapeCircle.r,
          }
          component.shapeRefined = shapeRefined
          component.graphicalFeature = {
            leftTopX,
            leftTopY,
            componentWidth,
            componentHeight
          }

          const { points, validPoints, d } = obtainIdealPointsForCircle(component)
          component.d = d
          component.sensorPositions = points
          component.sensorValidPositions = validPoints

        } else if (type === 'polygon') {
          const shapePolygon = shape as [number, number][]
          const leftPoint = minBy(shapePolygon, (p: [number, number]) => p[0]) as [number, number]
          const topPoint = minBy(shapePolygon, (p: [number, number]) => p[1]) as [number, number]
          const rightPoint = maxBy(shapePolygon, (p: [number, number]) => p[0]) as [number, number]
          const bottomPoint = maxBy(shapePolygon, (p: [number, number]) => p[1]) as [number, number]

          const componentWidth = rightPoint[0] - leftPoint[0]
          const componentHeight = bottomPoint[1] - topPoint[1]
          const leftTopX = leftPoint[0]
          const leftTopY = topPoint[1]
          const shapeRefined = shapePolygon.map(
            (p) => [p[0] - leftTopX, p[1] - leftTopY] as [number, number]
          )
          component.shapeRefined = shapeRefined
          component.graphicalFeature = {
            leftTopX,
            leftTopY,
            componentWidth,
            componentHeight
          }
          const { points, validPoints, d } = obtainIdealPoints(component)
          component.d = d
          component.sensorPositions = points
          component.sensorValidPositions = validPoints
        }


        // 如果是array，裁剪图片后扔到后端
        if (component.nArray > 1) {
          processArrayComponent(component, backgroundImageUrl.value)
        }

        //获取映射关系需要的参数
        const componentSensors = component.validSensors
        const initialMapping: { [pid: number]: number } = {}
        // intiail mapping
        // // group position by y
        const orderedValidPoints = orderingPoints(component)
        for (let i = 0; i < orderedValidPoints.length; i++) {
          const p = orderedValidPoints[i]
          initialMapping[p.pid] = i
        }
        const { mapping, finalValue } = fetchLayoutGreedy(
          component,
          initialMapping,
          groupsByType.value,
          weights.value
        )
        const links = getLinks(mapping, component, 'location')
        for (const pid in mapping) {
          component.mapping[pid] = componentSensors[mapping[pid]]
        }
        // console.log(links)
        component.links = links
        const communityPaths = getCommmunityPaths(links, component, component.d)
        component.hullPaths = communityPaths
        console.log(component.mapping)
      }
    })
    // console.log(structure)
    // const ps = [[10, 10], [14, 11], [36, 44], [10, 40]] as Point[]
    // console.log(getSmoothHull(ps, 5))
  }

  const data = ref({} as sensorData)

  const getdata = () => {
    isMonitoring.value = true
    const worker = new Worker('http://127.0.0.1:5173/src/worker/csvWorker.ts')
    const filePath = 'http://127.0.0.1:5173/src/assets/sample_data_resample_1T.csv'
    const interval = 1000 // 时间间隔（单位：毫秒）
    const serializedSensorNames = JSON.stringify(sensorNames.value)
    worker.onmessage = function (event) {
      const message = event.data

      if (message === '文件读取完成') {
        // 文件读取完成
        console.log('文件读取完成')
      } else {
        // 处理每行数据
        data.value = message
      }
    }

    worker.postMessage({ filePath, interval, serializedSensorNames })
  }

  const swapPosition = (i: number, j: number, name: string) => {
    // 把j换到i
    for (const c of structure.value) {
      if (c.name === name) {
        const tempName = c.mapping[i]
        c.mapping[i] = c.mapping[j]

        if (tempName) {
          c.mapping[j] = tempName
        } else {
          delete c.mapping[j]
        }

        const initialMapping: { [pid: number]: number } = {}
        // intiail mapping
        console.log(c.mapping)
        const componentSensors = c.validSensors
        for (let i = 0; i < c.sensorValidPositions.length; i++) {
          const p = c.sensorValidPositions[i]
          initialMapping[p[2]] = componentSensors.indexOf(c.mapping[p[2]])
        }

        const links = getLinks(initialMapping, c, 'location')
        console.log(links)
        c.links = links
        const communityPaths = getCommmunityPaths(links, c, c.d)
        c.hullPaths = communityPaths
      }
    }
  }

  const reLayout = (name: string) => {
    for (const c of structure.value) {
      if (c.name === name) {
        const componentSensors = c.validSensors
        const initialMapping: { [pid: number]: number } = {}
        // intiail mapping
        console.log(c.mapping)
        for (let i = 0; i < c.sensorValidPositions.length; i++) {
          const p = c.sensorValidPositions[i]
          initialMapping[p[2]] = componentSensors.indexOf(c.mapping[p[2]])
        }
        console.log(initialMapping)
        const { mapping, finalValue } = fetchLayoutGreedy(
          c,
          initialMapping,
          groupsByType.value,
          weights.value
        )
        const links = getLinks(mapping, c, 'location')
        c.links = links
        const communityPaths = getCommmunityPaths(links, c, c.d)
        c.hullPaths = communityPaths
        for (const pid in mapping) {
          c.mapping[pid] = componentSensors[mapping[pid]]
        }
      }
    }
  }

  // const startMonitor = () => {
  //   EventBus.emit('startMonitor')
  // }
  const setGlobalBackgroundImage = (imgUrl: string) => {
    backgroundImageUrl.value = imgUrl
  }

  const filterSensors = (removed: { [s: string]: boolean }) => {
    structure.value.forEach(c => {
      const componentSensors = flatten(c.sensorGroups[0].groups).filter(s => !(s in removed))
      c.validSensors = componentSensors
      c.nSensor = c.validSensors.length
      console.log(c.nSensor)
    })
  }

  const reLayoutTotally = () => {
    structure.value.forEach(c => {
      if (c.drew) {
        const componentSensors = c.validSensors
        if (c.shapeType === 'circle') {
          const { points, validPoints, d } = obtainIdealPointsForCircle(c)
          c.d = d
          c.sensorPositions = points
          c.sensorValidPositions = validPoints
        } else if (c.shapeType === 'polygon') {
          const { points, validPoints, d } = obtainIdealPoints(c)
          c.d = d
          c.sensorPositions = points
          c.sensorValidPositions = validPoints
        }

        console.log(c.nSensor)
        console.log(c.sensorPositions.length)
        console.log(c.sensorValidPositions.length)

        //获取映射关系需要的参数
        const initialMapping: { [pid: number]: number } = {}
        // intiail mapping
        // // group position by y
        const orderedValidPoints = orderingPoints(c)
        for (let i = 0; i < orderedValidPoints.length; i++) {
          const p = orderedValidPoints[i]
          initialMapping[p.pid] = i
        }
        console.log(orderedValidPoints)
        console.log(initialMapping)
        const { mapping, finalValue } = fetchLayoutGreedy(
          c,
          initialMapping,
          groupsByType.value,
          weights.value
        )
        const links = getLinks(mapping, c, 'location')
        c.mapping = {}
        for (const pid in mapping) {
          c.mapping[pid] = componentSensors[mapping[pid]]
        }
        // console.log(links)
        c.links = links
        const communityPaths = getCommmunityPaths(links, c, c.d)
        c.hullPaths = communityPaths
        console.log(c.mapping)
      }


    })
  }

  return {
    isMonitoring,
    structure,
    sensorNames,
    reLayout,
    getdata,
    swapPosition,
    data,
    setShape,
    flattenStructures,
    backgroundImageUrl,
    setGlobalBackgroundImage,
    filterSensors,
    reLayoutTotally
  }
})
