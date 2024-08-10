<template>
  <div
    class="component"
    :style="{
      left: `${gf.leftTopX - padding}px`,
      top: `${gf.leftTopY - padding}px`,
      width: `${gf.componentWidth + 2 * padding}px`,
      height: `${gf.componentHeight + 2 * padding}px`,
    }"
  >
    <div class="component-name">
      {{ props.component.name }}
    </div>
    <svg
      :width="gf.componentWidth + 2 * padding"
      :height="gf.componentHeight + 2 * padding"
      ref="chart"
    >
      <g :transform="`translate(${padding},${padding})`">
        <path :d="pathStyle" fill="transparent" stroke="#fff" />
        <g>
          <circle
            v-for="(p, i) in props.component.sensorPositions"
            :cx="p[0]"
            :cy="p[1]"
            r="props.component.d*0.4"
            :key="i"
            fill="#fff"
          />
        </g>
      </g>
    </svg>
  </div>
</template>

<script lang="ts">
import { useStructureStore } from '../../stores/structure'
import { onMounted, ref, computed, type PropType, nextTick, watch } from 'vue'
import type { sensorData } from '../../interface/sensorData'
import * as d3 from 'd3'
import { nums } from '../../interface/nums'
import EventBus from '../../../src/bus'
import { update } from 'lodash'

export default {
  name: 'demo-dd',
  props: {
    msg: {
      required: true,
      type: String,
    },
    component: {
      required: true,
      type: Object as PropType<MyComponent>,
    },
    data: {
      type: Object as PropType<sensorData>,
      default: {} as sensorData,
    },
  },

  setup(props) {
    let prevX = 0
    let prevY = 0
    const isDragging = ref(false)
    const startDraggingPoint = ref([0, 0])
    const dx = ref(0)
    const dy = ref(0)
    const padding = 20
    const chart = ref() //svg的引用
    const structureStore = useStructureStore()
    const radius = ref() //仪表盘半径
    const innerArc = ref() // 仪表盘 内边的条形宽度
    const littleinnerArc = ref() //仪表盘外边的条形宽度
    const gf = computed(() => props.component.graphicalFeature)
    const shapeRefined = computed(() =>
      props.component.shape.map(
        (p) => [p[0] - gf.value.leftTopX, p[1] - gf.value.leftTopY] as [number, number]
      )
    )

    const pathStyle = computed(() => {
      let d = ''
      shapeRefined.value.forEach((p, i) => {
        if (i === 0) {
          d += `M ${p[0]} ${p[1]} `
        } else if (i === shapeRefined.value.length - 1) {
          d += `L ${p[0]} ${p[1]} Z`
        } else {
          d += `L ${p[0]} ${p[1]} `
        }
      })
      return d
    })

    const anglelength = 220 // 仪表盘 度数
    let num: number[] = []

    const kedu: number[] = []
    for (let i = -anglelength / 2; i <= anglelength / 2; i += anglelength / 50) {
      kedu.push((i * Math.PI) / 180)
    }

    const colorScale = d3
      .scaleOrdinal()
      .domain(['Group 1', 'Group 2', 'Group 3', 'Group 4'])
      .range(['red', 'orange', 'yellow', 'green']) //仪表盘颜色比例尺

    // 指针位置点 计算
    const points = () => {
      // 顶点
      const upper = radius.value * 0.8 - innerArc.value
      // 两边  中间点
      const short = upper * 0.13
      // 两边点
      const both = short * 0.6
      return ['0,' + short, both + ',0', '0,' + -upper, -both + ',0']
    }


    const rotateTween = (a: number[]) => {
      return function (d: number) {
        return function (t: number) {
          //console.log("data/num[4]:",(data-num[0])/(num[4]-num[0]))
          return 'rotate(' + t * (-0.5 + (d - a[0]) / (a[4] - a[0])) * anglelength + ')'
        }
      }
    }
    const fillTween = (a: number[]) => {
      return function (d: number) {
        return function (t: number) {
          if(d==a[0])return colorScale(0)
          let i: number = 0
          while (i < num.length - 1 && a[i] - a[0] < (d - a[0]) * t) {
            i++
          }
          return colorScale(i-1)
        }
      }
    }

    const rectColor = (d: number) => {
      if(d==num[0])return colorScale('Group 0')
      let i = 0
      while (i < num.length -1 && num[i] < d) {
        i++
      }
      return colorScale(i - 1)
    }

    watch(
      () => props.data,
      (newValue) => {
        console.log('value changed:', newValue)
        paintDashboard()
      },
      { deep: true }
    )

    const paintDashboard = () => {
  
      const numLength = 100 // 仪表盘总长度
      radius.value = props.component.d * 0.4 //仪表盘半径
      innerArc.value = radius.value * 0.2 // 仪表盘 内边的条形宽度
      littleinnerArc.value = radius.value * 0.05 //仪表盘外边的条形宽度
      // 创建 扇形绘制器
      const arc = d3
        .arc()
        .outerRadius(radius.value * 0.8)
        .innerRadius(radius.value * 0.8 - innerArc.value)

      const arcTwo = d3
        .arc()
        .outerRadius(radius.value)
        .innerRadius(radius.value - littleinnerArc.value)
      let data: number
      const sensors = props.component.sensors
      const positions = props.component.sensorPositions
      // const distance = props.component.d // 每相邻两个一以
      console.log('paintDashboard', sensors)
      const oneDimensionSensors = sensors.flat() //将sensors转化为一维数组
      //console.log('oneDimensionSensors:', oneDimensionSensors)
      interface AngleDraw {
        startAngle: number
        endAngle: number
      }
      const angles = [0, 50, 70, 90, 100] //仪表盘刻度
      let angleDraw: AngleDraw[] = []
      angles.forEach((item: number, i: number) => {
        if (i !== angles.length - 1) {
          const angleS: number = (item / numLength) * anglelength
          const angleE: number = (angles[i + 1] / numLength) * anglelength
          angleDraw.push({
            startAngle: (angleS - anglelength / 2) * (Math.PI / 180),
            endAngle: (angleE - anglelength / 2) * (Math.PI / 180),
          })
        }
      })

      //将弧度分成五十份，得到50个刻度的弧度的位置

      //选择circle
      nextTick(() => {
        const svg = d3.select(chart.value)
        svg.selectAll('*').remove()
        //   <g :transform="`translate(${padding},${padding})`">
        //   <path :d="pathStyle" fill="transparent" stroke="#fff" />
        // </g>
        const g = svg.append('g').attr('transform', 'translate(' + padding + ',' + padding + ')')
        const path = g.append('path').attr('fill', 'transparent').attr('stroke', '#fff')
        path.attr('d', pathStyle.value)

        positions.forEach((item, i) => {
          const svg = d3.select(chart.value)
          const g = svg.append('g').attr('transform', 'translate(' + padding + ',' + padding + ')')
          const circle = g
            .append('circle')
            .attr('cx', item[0])
            .attr('cy', item[1])
            .attr('r', props.component.d * 0.4)
            .attr('key', i)
            .attr('fill', '#fff')
            .attr('class', 'circle')
          console.log(data)
          data = Number(structureStore.data[oneDimensionSensors[i] as keyof sensorData])
          //console.log('data', i, oneDimensionSensors[i], ':', data)

          // 分段值
          if (nums[oneDimensionSensors[i] as keyof sensorData] != '') {
            num = nums[oneDimensionSensors[i] as keyof sensorData]
              ?.split(',')
              .map((numStr) => Number(numStr)) as number[]
            // console.log('num', i, num)

            // 绘制仪表盘路径
            const path = g
              .append('g')
              .attr('transform', 'translate(' + positions[i][0] + ',' + positions[i][1] + ')')
              .selectAll()
              .data(angleDraw)
              .enter()
              .append('path')
              .attr('class', (d: AngleDraw, i: number) => ' arc-' + i)
              .attr('d', arc)
              .attr('fill', (d: AngleDraw, i: number) => colorScale(i))

            const pathTwo = g
              .append('g')
              .attr('transform', 'translate(' + positions[i][0] + ',' + positions[i][1] + ')')
              .selectAll()
              .data(angleDraw)
              .enter()
              .append('path')
              .attr('class', (d: AngleDraw, i: number) => ' arc-' + i)
              .attr('d', arcTwo)
              .attr('fill', (d: AngleDraw, i: number) => colorScale(i))
     
   
            const ticks = g
              .append('g')
              .attr('transform', 'translate(' + positions[i][0] + ',' + positions[i][1] + ')')
              .selectAll()
              .data(kedu)
              .enter()
              .append('g')
              .attr('class', 'ticks')
              .each(drawTicks)
              .each(drawLabels)

            //使用多边形绘制指针，先计算出指针个点坐标位置，通过旋转修改指针指向 0 点
            const pointer = g
              .append('g')
              .attr('transform', 'translate(' + positions[i][0] + ',' + positions[i][1] + ')')
              .selectAll()
              .data([data])
              .enter()
              .append('polygon')
              .attr('class', 'pointer')
              .attr('points', points)
              .attr('fill', colorScale('Group 0'))
              .attr('transform', 'rotate(' + -0.5 * anglelength + ')')
            const a = num
            pointer
              .transition()
              .duration(0)
              .attrTween('transform', rotateTween(a))
              .attrTween('fill', fillTween(a))

            // 添加矩形
            const rectWidth = 1 * radius.value // 矩形宽度
            const rectHeight = 0.5 * radius.value // 矩形高度
            const rectX = positions[i][0] - radius.value * 0.5 // 矩形左上角 X 坐标
            const rectY = positions[i][1] + radius.value * 0.4 // 矩形左上角 Y 坐标

            g.append('rect')
              .attr('x', rectX)
              .attr('y', rectY)
              .attr('width', rectWidth)
              .attr('height', rectHeight)
              .attr('fill', rectColor(data))
              .text('1')

            // 添加文本
            const textX = rectX + rectWidth / 2 // 文本中心 X 坐标
            const textY = rectY + rectHeight / 2 // 文本中心 Y 坐标

            g.append('text')
              .text(data)
              .attr('x', textX)
              .attr('y', textY)
              .attr('dy', '0.35em') // 文本垂直居中
              .attr('text-anchor', 'middle') // 文本水平居中
              .attr('fill', 'white')
              .attr('font-size', radius.value * 0.2 + 'px')
          } else {
            const c = g
              .append('circle')
              .attr('cx', item[0])
              .attr('cy', item[1])
              .attr('r', radius.value * 0.8)
              .attr('key', i)
              .attr('fill', 'red')
              .attr('class', 'circle')

            const text = g
              .append('text')
              .attr('x', item[0])
              .attr('y', item[1])
              .attr('text-anchor', 'middle')
              .attr('dy', '0.35em')
              .text(data)
              .attr('font-size', radius.value * 0.3 + 'px')
          }
        })
      })
    }
    function drawTicks(d: number, i: number) {
      if (i === 0 || i === 50) return
      const innerRadius =
        i % 5 === 0 ? radius.value * 0.8 - innerArc.value : radius.value * 0.8 - innerArc.value / 3
      d3.select(this)
        .append('line')
        .attr('stroke', 'black')
        .attr('stroke-width', 0.1)
        .attr('x1', Math.sin(d) * (radius.value * 0.8))
        .attr('y1', -Math.cos(d) * (radius.value * 0.8))
        .attr('x2', Math.sin(d) * innerRadius)
        .attr('y2', -Math.cos(d) * innerRadius)
    }

    function drawLabels(d: number, i: number) {
      let textAnchor = 'end'
      if (i === 25) {
        textAnchor = 'middle'
      }
      if (i % 5 === 0) {
        const textRadius = radius.value * 0.55
        d3.select(this)
          .append('text')
          .attr('class', 'label')
          .attr('x', Math.sin(d) * textRadius)
          .attr('y', -Math.cos(d) * textRadius)
          .attr('dy', 1)
          .attr('text-anchor', d < -0.01 ? 'start' : textAnchor)
          .text((i / 50) * (num[4] - num[0]) + num[0])
          .attr('fill', 'black')
          .attr('font-size', radius.value*0.07+'px')
      }
      if (i === 49) {
        const textRadius = radius.value * 0.55
        d3.select(this)
          .append('text')
          .attr('class', 'label')
          .attr('x', Math.sin(2 * kedu[49] - kedu[48]) * textRadius)
          .attr('y', -Math.cos(d) * textRadius)
          .attr('dy', 1)
          .attr('text-anchor', d < -0.01 ? 'start' : textAnchor)
          .text(num[4])
          .attr('fill', 'black')
          .attr('font-size', radius.value*0.07+'px')
      }
    }

    onMounted(() => {
      console.log('mounted')
      // EventBus.on('startMonitor', () => {
      //   paintDashboard()
      // })
    })

    // // 切换选中状态
    // const toggleSelection = (index: number) => {
    //   isSelected.value[index] = !isSelected.value[index];
    // };

    // // 获取圆圈颜色
    // const getCircleColor = (index: number) => {
    //   return isSelected.value[index] ? 'green' : 'white';
    // };

    const startDrag = (event: MouseEvent) => {
      console.log('startDrag', event)
      event.stopPropagation()
      isDragging.value = true
      startDraggingPoint.value = [event.pageX, event.pageY]
    }
    const dragging = (event: MouseEvent) => {
      if (isDragging.value) {
        dx.value = event.pageX - startDraggingPoint.value[0] + prevX
        dy.value = event.pageY - startDraggingPoint.value[1] + prevY
      }
    }
    const stopDrag = () => {
      prevX = dx.value
      prevY = dy.value
      isDragging.value = false;
    }

    return {
      dx,
      dy,
      chart,
      gf,
      structureStore,
      props,
      pathStyle,
      padding,
      startDrag,
      dragging,
      stopDrag
    }
  },
}
</script>
<style scoped lang="scss">
.component {
  position: absolute;
  height: 100%;
  width: 100%;

  .component-name {
    position: absolute;
    width: 100px;
    height: 30px;
    top: 100%;
    left: calc(50% - 50px);
    font-weight: 600;
    line-height: 30px;
    color: #fff;
  }
}
</style>
