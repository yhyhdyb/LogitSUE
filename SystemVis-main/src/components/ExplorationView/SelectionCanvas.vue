<template>
  <div class="selection-canvas">
    <svg
      width="100%"
      height="1240"
      v-if="showSVG"
      :style="{
        position: 'absolute',
      }"
      class="canvas"
      @click="onAddControlPoint($event)"
      @mousemove="onMovingControlPoint($event)"
    >
      <g>
        <polygon :points="polygonPoints" fill="transparent" stroke="#fff" stroke-width="1" />
        <circle v-for="(p, i) in shape" :cx="p[0]" :cy="p[1]" r="4" :key="i" fill="#fff" />
        <circle
          :cx="shapeForCircle.cx"
          :cy="shapeForCircle.cy"
          :r="shapeForCircle.r"
          fill="none"
          stroke="#fff"
        />
      </g>
    </svg>
    <div class="menu">
      <div
        class="btn-div"
        @click="onDrawing(c)"
        v-for="c in structureStore.structure"
        :key="c.name"
      >
        {{ c.name }} * {{ c.nArray }}
      </div>
      <div class="btn-div" @click="onStartMonitor">START</div>
      <div class="btn-div" @click="openFilePicker">选择背景图片</div>
      <input
        class="file_input"
        type="file"
        accept="image/*"
        style="display: none"
        @change="setBackgroundImage"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { useStructureStore } from '../../stores/structure'
import { onMounted, ref, computed } from 'vue'

export default {
  name: 'selection-canvas',
  setup() {
    const isControlPressed = ref(false)
    const structureStore = useStructureStore()
    const shape = ref<[number, number][]>([])
    const shapeForCircle = ref<ShapeForCircle>({ r: 0, cx: 0, cy: 0 })
    const componentNameDrawed = ref('')
    const showSVG = ref(false)
    const isDrawing = ref(false)

    const polygonPoints = computed(() => {
      return shape.value.map((point) => `${point[0]},${point[1]}`).join(' ')
    })

    const onDrawing = (c: MyComponent) => {
      if (componentNameDrawed.value === c.name) {
        componentNameDrawed.value = ''
        isDrawing.value = false
      } else {
        componentNameDrawed.value = c.name
        showSVG.value = true
      }
    }

    const onMovingControlPoint = (e: MouseEvent) => {
      if (isControlPressed.value) {
        // 如果画的是circle
        const dx = e.pageX - shapeForCircle.value.cx
        const dy = e.pageY - shapeForCircle.value.cy
        shapeForCircle.value.r = Math.sqrt(dx * dx + dy * dy)
      } else {
        // 如果画的是polygon
        if (isDrawing.value) {
          shape.value[shape.value.length - 1] = [e.pageX, e.pageY]
        }
      }
    }

    const onAddControlPoint = (e: MouseEvent) => {
      if (isControlPressed.value) {
        // 如果画的是circle
        shapeForCircle.value.cx = e.pageX
        shapeForCircle.value.cy = e.pageY
      } else {
        // 如果画的是polygon
        if (isDrawing.value) {
          shape.value.push([e.pageX, e.pageY])
        }
        if (componentNameDrawed.value && !isDrawing.value) {
          shape.value = [
            [e.pageX, e.pageY],
            [e.pageX, e.pageY],
          ]
          isDrawing.value = true
        }
      }
    }

    const finishDrawing = () => {
      if (shapeForCircle.value.r > 0) {
        // 如果画的是circle
        structureStore.setShape(shapeForCircle.value, componentNameDrawed.value, 'circle')
        shapeForCircle.value = { r: 0, cx: 0, cy: 0 }
      } else {
        // 如果画的是polygon
        shape.value = shape.value.slice(0, shape.value.length - 1)
        if (shape.value.length >= 3) {
          structureStore.setShape(shape.value, componentNameDrawed.value, 'polygon')
        }
        componentNameDrawed.value = ''
        isDrawing.value = false
        showSVG.value = false
        shape.value = []
      }
    }

    const onStartMonitor = () => {
      // structureStore.startMonitor()
      structureStore.getdata()
    }

    const openFilePicker = () => {
      const file_input_btn = document.querySelector('.file_input') as HTMLElement
      file_input_btn.click()
    }

    const setBackgroundImage = (event: Event) => {
      const inputElement = event.target as HTMLInputElement
      if (inputElement.files && inputElement.files.length > 0) {
        const file = inputElement.files[0]
        const reader = new FileReader()

        reader.onload = () => {
          const imageUrl = reader.result as string
          const backgroundElement = document.querySelector('.background-image') as HTMLElement
          backgroundElement.style.backgroundImage = `url(${imageUrl})`
          structureStore.setGlobalBackgroundImage(imageUrl)
          const backgroundBlackElement = document.querySelector('#black') as HTMLElement
          backgroundBlackElement.style.backgroundColor = `rgba(0, 0, 0, 0.5)`
        }

        reader.readAsDataURL(file)
      }
    }

    onMounted(() => {
      document.addEventListener('keydown', (e) => {
        // 画完polygon
        if (e.code === 'Space' && isDrawing.value) {
          finishDrawing()
        }
        if (e.key === 'Control') {
          // 开始画circle
          console.log('ctrl is pressed')
          isControlPressed.value = true
        }
      })
      document.addEventListener('keyup', (e) => {
        // 画完circle
        if (e.key === 'Control') {
          console.log('ctrl is not pressed')
          isControlPressed.value = false
          finishDrawing()
        }
      })
    })

    return {
      shapeForCircle,
      isControlPressed,
      showSVG,
      isDrawing,
      shape,
      structureStore,
      componentNameDrawed,
      polygonPoints,
      onMovingControlPoint,
      onDrawing,
      onAddControlPoint,
      onStartMonitor,
      openFilePicker,
      setBackgroundImage,
    }
  },
}
</script>
<style scoped lang="scss">
.selection-canvas {
  position: absolute;
  width: 100%;
  height: 50px;

  .menu {
    position: absolute;
    height: 50px;
    width: 100%;
    background-color: #4f709c;
    color: #4f709c;

    .btn-div {
      position: relative;
      width: 140px;
      height: calc(100% - 20px);
      margin: 10px;
      background-color: #fff;
      text-align: center;
      line-height: 30px;
      // transition: all 300ms;
      font-weight: 400;
      user-select: none;
      float: left;
    }

    .btn-div:hover {
      font-weight: 600;
    }

    .clicked {
      font-weight: 600;
    }
  }
}
</style>
