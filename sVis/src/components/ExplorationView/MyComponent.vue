<template>
  <div
    class="component"
    :style="{
      left: `${leftTopX - padding}px`,
      top: `${leftTopY - padding}px`,
      width: `${componentWidth + 2 * padding}px`,
      height: `${componentHeight + 2 * padding}px`,
    }"
  >
    <svg :width="componentWidth + 2 * padding" 
    :height="componentHeight + 2 * padding">
      <g :transform="`translate(${padding},${padding})`">
        <path :d="pathStyle" fill="transparent" stroke="#fff" />
        <circle v-for="(p, i) in positions" :cx="p[0]" :cy="p[1]" r="10" :key="i" fill="#fff" />
      </g>
    </svg>
  </div>
</template>

<script lang="ts">
import { useStructureStore } from '../../stores/structure'
import { obtainIdealPoints } from '../../utils/generateGrids'
import { onMounted, ref, computed, type PropType } from 'vue'
import { minBy, maxBy } from 'lodash'
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
  },
  setup(props) {
    const padding = 20
    let positions = ref([] as [number, number][])
    const structureStore = useStructureStore()
    const leftPoint = computed(
      () => minBy(props.component.shape, (p: [number, number]) => p[0]) as [number, number]
    )
    const topPoint = computed(
      () => minBy(props.component.shape, (p: [number, number]) => p[1]) as [number, number]
    )
    const rightPoint = computed(
      () => maxBy(props.component.shape, (p: [number, number]) => p[0]) as [number, number]
    )
    const bottomPoint = computed(
      () => maxBy(props.component.shape, (p: [number, number]) => p[1]) as [number, number]
    )

    const componentWidth = computed(() => rightPoint.value[0] - leftPoint.value[0])
    const componentHeight = computed(() => bottomPoint.value[1] - topPoint.value[1])
    const leftTopX = computed(() => leftPoint.value[0])
    const leftTopY = computed(() => topPoint.value[1])

    const shapeRefined = computed(() =>
      props.component.shape.map(
        (p) => [p[0] - leftTopX.value, p[1] - leftTopY.value] as [number, number]
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
    console.log(bottomPoint)

    onMounted(() => {
      console.log('mounted')
      const { points, d } = obtainIdealPoints(
        0,
        0,
        componentWidth.value,
        componentHeight.value,
        shapeRefined.value,
        props.component.nSensor
      )
      positions.value = points.slice(0, props.component.nSensor)
      console.log(points, d)
      // new ThreeJs();
      // scene = new THREE.Scene();
      // setCamera();
      // setRenderer();
      // setCube();
      // animate();
    })

    return {
      structureStore,
      props,
      pathStyle,
      positions,
      componentWidth,
      componentHeight,
      leftTopX,
      leftTopY,
      padding,
    }
  },
}
</script>
<style scoped lang="scss">
.component {
  position: absolute;
  // border: 1px solid #fff;
}
</style>
