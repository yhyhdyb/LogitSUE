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
    <div class="widget">
      <div class="functions" v-show="!structureStore.isMonitoring" @click="reLayout">RE-LAYOUT</div>
      <div class="component-name">
        {{ props.component.name }}
      </div>
    </div>
    <svg :width="gf.componentWidth + 2 * padding" :height="gf.componentHeight + 2 * padding">
      <g :transform="`translate(${padding},${padding})`">
        <g class="links">
          <!-- <line
            v-for="link in props.component.links"
            :key="`${link[0]},${link[1]}`"
            :x1="props.component.sensorPositions[link[0]][0]"
            :y1="props.component.sensorPositions[link[0]][1]"
            :x2="props.component.sensorPositions[link[1]][0]"
            :y2="props.component.sensorPositions[link[1]][1]"
            style="stroke-width: 0.5; stroke: #fff; stroke-opacity: 1"
            stroke-dasharray="4"
          /> -->
          <path
            v-for="(path, i) in props.component.hullPaths"
            :d="path"
            :key="i"
            fill="rgba(255,255,255,0.1)"
            stroke="none"
            stroke-width="0"
          />
        </g>
      </g>
    </svg>

    <svg
      :width="gf.componentWidth + 2 * padding"
      :height="gf.componentHeight + 2 * padding"
      ref="chart"
    ></svg>
    <svg
      :width="gf.componentWidth + 2 * padding"
      :height="gf.componentHeight + 2 * padding"
      @mousemove="dragPosition"
    >
      <g :transform="`translate(${padding},${padding})`">
        <path
          v-show="!structureStore.isMonitoring"
          :d="pathStyle"
          fill="transparent"
          stroke="#fff"
        />
        <circle
          v-if="props.component.shapeType === 'circle' && !structureStore.isMonitoring"
          :r="circleStype.r"
          :cx="circleStype.cx"
          :cy="circleStype.cy"
          fill="none"
          stroke="#fff"
        />
        <g class="sensor-name">
          <text
            v-for="sensor in sensors"
            :key="sensor.name"
            :x="sensor.x"
            :y="sensor.y + props.component.d * 0.4"
            fill="#fff"
            :font-size="`${props.component.d * 0.4 * 0.4}px`"
            :textLength="props.component.d * 0.4 * 2"
            lengthAdjust="spacingAndGlyphs"
            dy="0.35em"
            text-anchor="middle"
          >
            {{ sensor.name }}
          </text>
        </g>
        <g class="circle-placeholder" v-show="!structureStore.isMonitoring">
          <circle
            class="dragging-hint"
            v-if="isPositionDragging"
            fill="#fff"
            :cx="positionDraggingHintXY.x"
            :cy="positionDraggingHintXY.y"
            r="10"
            opacity="0.4"
          />
          <circle
            @mousedown="startDragPosition($event, sensor.pid)"
            v-for="sensor in sensors"
            :cx="sensor.x"
            :cy="sensor.y"
            :r="10"
            :key="sensor.name"
            fill="#fff"
          />
          <rect
            @mouseup="endDragPosition(i)"
            @mouseenter="hoveringRect(i)"
            v-show="isPositionDragging"
            v-for="(p, i) in props.component.sensorPositions"
            :x="p[0] - props.component.d / 2"
            :y="p[1] - props.component.d / 2"
            :width="props.component.d"
            :height="props.component.d"
            :key="i"
            :style="{
              opacity: hoveredRectId === i ? 1 : 0,
              fill: 'rgba(0,0,0,0)',
              'stroke-width': 1,
              stroke: '#fff',
            }"
          />
        </g>
      </g>
    </svg>
  </div>
</template>

<script lang="ts">
import { useStructureStore } from '../../stores/structure'
import { onMounted, ref, computed, type PropType, nextTick, watch } from 'vue'
import type { sensorData } from '../../interface/coal/sensorData'
import * as d3 from 'd3'
import { nums } from '../../interface/coal/num'

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
    const hoveredRectId = ref(-1)
    const isPositionDragging = ref(false)
    const isPositionDraggingId = ref(-1)
    const positionDraggingHintXY = ref({
      x: 0,
      y: 0,
    })

    const sensors = computed(() => {
      const sensors = []
      console.log(props.component.mapping)
      console.log(props.component.sensorPositions)
      for (const pid in props.component.mapping) {
        const sensorName = props.component.mapping[pid]
        if (sensorName) {
          sensors.push({
            name: sensorName,
            x: props.component.sensorPositions[parseInt(pid)][0],
            y: props.component.sensorPositions[parseInt(pid)][1],
            pid: parseInt(pid),
          })
        }
      }
      return sensors
    })

    const reLayout = () => {
      structureStore.reLayout(props.component.name)
    }
    const hoveringRect = (id: number) => {
      if (isPositionDragging.value) {
        hoveredRectId.value = id
      }
    }
    const startDragPosition = (e: MouseEvent, i: number) => {
      isPositionDragging.value = true
      isPositionDraggingId.value = i
    }

    const dragPosition = (e: MouseEvent) => {
      if (isPositionDragging.value) {
        positionDraggingHintXY.value.x = e.pageX - gf.value.leftTopX
        positionDraggingHintXY.value.y = e.pageY - gf.value.leftTopY
      }
    }

    const endDragPosition = (target_i: number) => {
      structureStore.swapPosition(target_i, isPositionDraggingId.value, props.component.name)

      isPositionDragging.value = false
      hoveredRectId.value = -1
      positionDraggingHintXY.value.x = 0
      positionDraggingHintXY.value.y = 0
      isPositionDraggingId.value = -1
    }

    const pathStyle = computed(() => {
      let d = ''
      if (props.component.shapeType === 'polygon') {
        const shapeRefined = props.component.shapeRefined as [number, number][]
        shapeRefined.forEach((p, i) => {
          if (i === 0) {
            d += `M ${p[0]} ${p[1]} `
          } else if (i === shapeRefined.length - 1) {
            d += `L ${p[0]} ${p[1]} Z`
          } else {
            d += `L ${p[0]} ${p[1]} `
          }
        })
      }
      return d
    })

    const circleStype = computed(() => {
      const shapeRefined = props.component.shapeRefined as ShapeForCircle
      return {
        cx: shapeRefined.cx,
        cy: shapeRefined.cy,
        r: shapeRefined.r,
      }
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
      .range(['#339900', '#CEFF6C', '#FF9966', '#CC3300']) //仪表盘颜色比例尺

    // 指针位置点 计算
    const points = () => {
      // 顶点
      const upper = radius.value - littleinnerArc.value * 3
      // 两边  中间点
      const short = upper * 0.13
      // 两边点
      const both = short * 0.9
      //return ['0,' + short, both + ',0', '0,' + -upper, -both + ',0',]
      return [
        short * 0.5 + ',' + 0,
        short * 0.5 + ',' + -upper * 0.7,
        both + ',' + -upper * 0.8,
        '0,' + -upper,
        -both + ',' + -upper * 0.8,
        -short * 0.5 + ',' + -upper * 0.7,
        -short * 0.5 + ',' + 0,
      ]
    }

    const rotateTween = (a: number[]) => {
      return function (d: number) {
        return function (t: number) {
          //console.log("data/num[4]:",(data-num[0])/(num[4]-num[0]))
          return 'rotate(' + t * (-0.5 + (d - a[1]) / (a[2] - a[1])) * anglelength + ')'
        }
      }
    }
    const fillTween = (a: number[]) => {
      return function (d: number) {
        return function (t: number) {
          if (d - a[1] <= (a[2] - a[1]) * 0.25) return colorScale('Group 0')

          let i: number = 1
          while (i <= 4 && (a[2] - a[1]) * 0.25 * i <= d - a[1]) {
            i++
          }
          return colorScale('Group ' + i)
        }
      }
    }

    const rectColor = (d: number) => {
      if (d - num[1] <= (num[2] - num[1]) * 0.25) return colorScale('Group 0')
      let i = 1
      while (i <= 4 && num[1] + (num[2] - num[1]) * 0.25 * i <= d) {
        i++
      }
      return colorScale('Group ' + i)
    }

    watch(
      () => props.data,
      (newValue) => {
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
      // const arc = d3
      //   .arc()
      //   .outerRadius(radius.value * 0.8)
      //   .innerRadius(radius.value * 0.8 - innerArc.value)

      const arcTwo = d3
        .arc()
        .outerRadius(radius.value - littleinnerArc.value * 2)
        .innerRadius(radius.value - littleinnerArc.value * 3)

      // 定义弧形的参数
      // const startAngle = -110; // 起始角度
      // const endAngle = 110; // 结束角度
      const innerRadius = radius.value - littleinnerArc.value * 3 // 内半径
      const angleDrawTwo: AngleDraw[] = [
        { startAngle: -110 * (Math.PI / 180), endAngle: 110 * (Math.PI / 180) },
      ]

      const arcGenerator = d3
        .arc()
        .innerRadius(innerRadius * 0.95)
        .outerRadius(innerRadius)
      // .startAngle((startAngle * Math.PI) / 180) // 将角度转换为弧度
      // .endAngle((endAngle * Math.PI) / 180);

      const startAngleRadians = -110 * (Math.PI / 180)
      const endAngleRadians = 110 * (Math.PI / 180)
      const startX = -Math.sin(startAngleRadians) * innerRadius
      const startY = -Math.cos(startAngleRadians) * innerRadius
      const endX = -Math.sin(endAngleRadians) * innerRadius
      const endY = -Math.cos(endAngleRadians) * innerRadius

      let data: number
      // const sensors = props.component.sensors
      const positions = props.component.sensorPositions
      // const distance = props.component.d // 每相邻两个一以
      // console.log('paintDashboard', sensors)
      // const oneDimensionSensors = sensors.flat() //将sensors转化为一维数组
      //console.log('oneDimensionSensors:', oneDimensionSensors)
      interface AngleDraw {
        startAngle: number
        endAngle: number
      }
      const angles = [0, 25, 50, 75, 100] //仪表盘刻度
      let angleDraw: AngleDraw[] = []
      angles.forEach((item: number, i: number) => {
        if (i !== angles.length - 1) {
          const angleS: number = (item / numLength) * anglelength
          const angleE: number = (angles[i + 1] / numLength) * anglelength
          angleDraw.push({
            startAngle:
              i == 0
                ? (angleS - anglelength / 2) * (Math.PI / 180)
                : (angleS - anglelength / 2) * (Math.PI / 180) +
                  anglelength * (Math.PI / 180) * 0.02,
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
        // </g>       // const g = svg.append('g').attr('transform', 'translate(' + padding + ',' + padding + ')')
        // const path = g.append('path').attr('fill', 'transparent').attr('stroke', '#fff')
        // path.attr('d', pathStyle.value)

        positions.forEach((item, i) => {
          if (!props.component.mapping[i]) {
            return
          }

          const svg = d3.select(chart.value)
          const g = svg.append('g').attr('transform', 'translate(' + padding + ',' + padding + ')')
          const circle = g
            .append('circle')
            .attr('cx', item[0])
            .attr('cy', item[1])
            .attr('r', props.component.d * 0.4)
            .attr('key', i)
            .attr('fill', 'none')
            .attr('class', 'circle')
          data = Number(structureStore.data[props.component.mapping[i] as keyof sensorData])

          // 添加矩形
          const rectWidth = 1 * radius.value // 矩形宽度
          const rectX = positions[i][0] - radius.value * 0.5 // 矩形左上角 X 坐标
          const rectY = positions[i][1] + radius.value * 0.4 // 矩形左上角 Y 坐标

          // 添加文本
          const textX = rectX + rectWidth / 2 // 文本中心 X 坐标
          const textY = rectY + rectWidth / 10 // 文本中心 Y 坐标

          console.log(props.component.mapping[i])
          console.log(props.component.mapping[i] as keyof sensorData)
          console.log(nums[props.component.mapping[i] as keyof sensorData])
          console.log(nums)
          if (
            nums[props.component.mapping[i] as keyof sensorData][0] != 'b' &&
            nums[props.component.mapping[i] as keyof sensorData][0] != 'c'
          ) {
            num = nums[props.component.mapping[i] as keyof sensorData]
              ?.split(',')
              .map((numStr) => Number(numStr)) as number[]
            // console.log('num', i, num)

            const pathTwo = g
              .append('g')
              .attr('transform', 'translate(' + positions[i][0] + ',' + positions[i][1] + ')')
              .selectAll()
              .data(angleDraw)
              .enter()
              .append('path')
              .attr('class', (d: AngleDraw, i: number) => ' arc-' + i)
              .attr('d', arcTwo)
              .attr('fill', (d: AngleDraw, i: number) => colorScale(i - 1))

            // 绘制弧形路径
            const pathThree = g
              .append('g')
              .attr('transform', 'translate(' + positions[i][0] + ',' + positions[i][1] + ')')
              .selectAll()
              .data(angleDrawTwo)
              .enter()
              .append('path')
              .attr('class', ' arc')
              .attr('d', arcGenerator)
              .attr('fill', '#fff')

            // 绘制圆心至起始点的连线
            g.append('g')
              .attr('transform', 'translate(' + positions[i][0] + ',' + positions[i][1] + ')')
              .append('line')
              .attr('x1', 0)
              .attr('y1', 0)
              .attr('x2', startX)
              .attr('y2', startY)
              .attr('stroke', '#fff')
              .attr('stroke-width', radius.value * 0.04)

            // 绘制圆心至结束点的连线
            g.append('g')
              .attr('transform', 'translate(' + positions[i][0] + ',' + positions[i][1] + ')')
              .append('line')
              .attr('x1', 0)
              .attr('y1', 0)
              .attr('x2', endX)
              .attr('y2', endY)
              .attr('stroke', '#fff')
              .attr('stroke-width', radius.value * 0.04)

            // const ticks = g
            //   .append('g')
            //   .attr('transform', 'translate(' + positions[i][0] + ',' + positions[i][1] + ')')
            //   .selectAll()
            //   .data(kedu)
            //   .enter()
            //   .append('g')
            //   .attr('class', 'ticks')
            //   .each(drawTicks)
            //   .each(drawLabels)

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
              .attr('fill', colorScale(0))
              .attr('transform', 'rotate(' + -0.5 * anglelength + ')')
            const a = num
            pointer
              .transition()
              .duration(0)
              .attrTween('transform', rotateTween(a))
              .attrTween('fill', fillTween(a))

            const text = g
              .append('text')
              .text(String(data))
              .attr('x', textX)
              .attr('y', textY)
              .attr('dy', '0.35em') // 文本垂直居中
              .attr('text-anchor', 'middle') // 文本水平居中
              .attr('fill', rectColor(data))
              .style('font-weight', 'bold')
              .attr('wdith', radius.value * 2)
              .attr('height', radius.value)
            //  .attr('font-size', radius.value * 0.4 + 'px').attr('lengthAdjust', 'spacingAndGlyphs')
            // .attr('textLength',radius.value*2)
            const textLength = text.node().getComputedTextLength()

            if (textLength < radius.value * 4) {
              // 如果文本长度不超过期望的宽度，设置文本框宽度为文本实际长度
              text.attr('font-size', radius.value * 0.4 + 'px')
            } else {
              // 如果文本长度超过期望的宽度，设置文本框宽度为期望的宽度
              text.attr('textLength', radius.value * 2)
              text.attr('lengthAdjust', 'spacingAndGlyphs')
              text.attr('font-size', radius.value * 0.4 + 'px')
            }
          } else if (nums[props.component.mapping[i] as keyof sensorData][0] == 'b') {
            if (data == 1) {
              g.append('circle')
                .attr('cx', item[0])
                .attr('cy', item[1])
                .attr('r', radius.value * 0.5)
                .attr('key', i)
                .attr('fill', '#fff')
                .attr('class', 'circle')

              g.append('text')
                .attr('x', item[0])
                .attr('y', item[1])
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .text('On')
                .attr('font-size', radius.value * 0.4 + 'px')
                .style('font-weight', 'bold')
                .attr('pointer-events', 'none')
            } else {
              const arcGenerator = d3
                .arc()
                .innerRadius(radius.value * 0.4)
                .outerRadius(radius.value * 0.5)
                .startAngle(0)
                .endAngle(2 * Math.PI)
              const path = g
                .append('g')
                .attr('transform', 'translate(' + positions[i][0] + ',' + positions[i][1] + ')')
                .append('path')
                .attr('class', ' arc')
                .attr('d', arcGenerator)
                .attr('fill', '#fff')

              g.append('text')
                .attr('x', item[0])
                .attr('y', item[1])
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .text('Off')
                .attr('font-size', radius.value * 0.4 + 'px')
                .style('font-weight', 'bold')
                .attr('fill', '#fff')
            }
          } else {
            const rectwidth = radius.value * 1.4
            const rectheight = radius.value * 0.8
            g.append('rect')
              .attr('x', item[0] - rectwidth / 2)
              .attr('y', item[1] - rectheight / 2)
              .attr('width', rectwidth)
              .attr('height', rectheight)
              .attr('stroke', '#fff')
              .attr('fill', 'none')

            // const maxDataCharacters = 6;
            // let displayedData = String(data)
            // if (displayedData.length > maxDataCharacters) {
            //   displayedData = String(data).slice(0, maxDataCharacters) + "..."; // 超过最大字符数时，截取部分文本并添加...
            // }
            // let res=displayedData
            g.append('text')
              .attr('x', item[0])
              .attr('y', item[1])
              .attr('text-anchor', 'middle')
              .attr('dy', '0.35em')
              .text(data)
              .attr('font-size', radius.value * 0.4 + 'px')
              .style('font-weight', 'bold')
              .attr('fill', '#fff')
          }
        })
      })
    }
    // function drawTicks(d: number, i: number) {
    //   if (i === 0 || i === 50) return
    //   const innerRadius =
    //     i % 5 === 0 ? radius.value * 0.8 - innerArc.value : radius.value * 0.8 - innerArc.value / 3
    //   d3.select(this)
    //     .append('line')
    //     .attr('stroke', 'black')
    //     .attr('stroke-width', 0.1)
    //     .attr('x1', Math.sin(d) * (radius.value * 0.8))
    //     .attr('y1', -Math.cos(d) * (radius.value * 0.8))
    //     .attr('x2', Math.sin(d) * innerRadius)
    //     .attr('y2', -Math.cos(d) * innerRadius)
    // }

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
          .text((i / 50) * (num[2] - num[1]) + num[1])
          .attr('fill', 'black')
          .attr('font-size', radius.value * 0.07 + 'px')
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
          .text(num[2])
          .attr('fill', 'black')
          .attr('font-size', radius.value * 0.07 + 'px')
      }
    }

    const startDrag = (event: MouseEvent) => {
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
      isDragging.value = false
    }

    return {
      radius,
      circleStype,
      dx,
      dy,
      chart,
      gf,
      structureStore,
      props,
      pathStyle,
      padding,
      isPositionDragging,
      positionDraggingHintXY,
      hoveredRectId,
      sensors,
      startDrag,
      dragging,
      stopDrag,
      endDragPosition,
      startDragPosition,
      dragPosition,
      hoveringRect,
      reLayout,
    }
  },
}
</script>
<style scoped lang="scss">
.component {
  position: absolute;
  height: 100%;
  width: 100%;

  .widget {
    position: absolute;
    width: 100px;
    height: 52px;
    top: calc(50% - 13px);
    left: calc(100% - 20px);

    .functions {
      position: relative;
      width: 100px;
      height: 26px;
      background-color: #fff;
      border: 1px;
      font-weight: 600;
      line-height: 26px;
      color: #000;
      text-align: center;
      border-radius: 5px;
      cursor: pointer;
    }

    .component-name {
      position: relative;
      width: 100px;
      height: 26px;
      font-weight: 600;
      line-height: 26px;
      color: #fff;
      text-align: center;
      user-select: none;
    }
  }

  svg {
    position: absolute;
  }

  text {
    user-select: none;
  }
}
</style>
