import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { sensorData } from '@/interface/sensorData'
import { obtainIdealPoints } from '../utils/generateGrids'
import { minBy, maxBy, cloneDeep } from 'lodash'
import EventBus from '../../src/bus'
import { batterySensorNames, batteryStructure } from '../data/battery'

export const useStructureStore = defineStore('structure', () => {
  const structure = ref(batteryStructure)
  const flattenStructures = computed(() => {
    let flattenOnes = [] as MyComponent[]
    for (const component of structure.value) {
      flattenOnes = flattenOnes.concat(new Array(component.nArray).fill(0).map((_, i) => {
        const c = cloneDeep(component)
        for (const p of c.shape) {
          p[0] += i * 200
          p[1] += i * 200
        }
        // for (const p of c.sensorPositions) {
        //   p[0] += i * 200
        //   p[1] += i * 200
        // }
        c.graphicalFeature.leftTopX += i * 200
        c.graphicalFeature.leftTopY += i * 200
        return c
      }) as MyComponent[])
    }
    return flattenOnes
  })

  // 添加 isSelected 属性给每个传感器
  // structure.value.forEach(component => {
  //   component.isSelected = new Array<boolean>(
  //     component.sensors.reduce((total, group) => total + group.length, 0)
  //   ).fill(false);
  // });

  // 环境反馈1 / 2 / 3 / 4 / 5 / 6
  // 整车设定
  // 整车反馈
  // 车辆运行模式 / 充电状态
  // 累计续驶里程
  // 锂电母线电压 / 电流
  // 回充/放电电流超限
  const sensorNames = ref(batterySensorNames)
  // const doubleCount = computed(() => count.value * 2)
  // function increment() {
  //   count.value++
  // }
  // const toggleSelection = (index: number) => {
  //   structure.value[index].isSelected = !structure.value[index].isSelected
  // }
  const setCircle = (center: [number, number], radius: number, name: string) => {
    console.log('setCircle', center, radius)
    structure.value.forEach(component => {
      if (component.name === name) {
        component.isCircle = true
        component.center = center
        component.radius = radius
        component.drew = true
      }
    });
  }

  const setShape = (shape: [number, number][], name: string) => {
    console.log('setShape', shape)
    structure.value.forEach(component => {
      if (component.name === name) {
        component.shape = shape
        component.drew = true

        const leftPoint = minBy(shape, (p: [number, number]) => p[0]) as [number, number]
        const topPoint = minBy(shape, (p: [number, number]) => p[1]) as [number, number]
        const rightPoint = maxBy(shape, (p: [number, number]) => p[0]) as [number, number]
        const bottomPoint = maxBy(shape, (p: [number, number]) => p[1]) as [number, number]

        const componentWidth = rightPoint[0] - leftPoint[0]
        const componentHeight = bottomPoint[1] - topPoint[1]
        const leftTopX = leftPoint[0]
        const leftTopY = topPoint[1]
        const shapeRefined = shape.map(
          (p) => [p[0] - leftTopX, p[1] - leftTopY] as [number, number]
        )
        const { points, d } = obtainIdealPoints(
          0,
          0,
          componentWidth,
          componentHeight,
          shapeRefined,
          component.nSensor
        )
        component.d = d
        component.sensorPositions = points.slice(0, component.nSensor)
        component.graphicalFeature = { leftTopX, leftTopY, componentWidth, componentHeight }
      }
    });
  }

  const data = ref({} as sensorData)

  const getdata = () => {
    const worker = new Worker('http://127.0.0.1:5173/src/worker/csvWorker.ts')
    const filePath = 'http://127.0.0.1:5173/src/assets/M15.csv'
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
        console.log('getting data', data.value)
        //console.log('data:', data)
      }
    }

    worker.postMessage({ filePath, interval, serializedSensorNames })
  }

  // const startMonitor = () => {
  //   EventBus.emit('startMonitor')
  // }

  return { structure, sensorNames, getdata, data, setShape, flattenStructures, setCircle }
})
