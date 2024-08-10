<!-- eslint-disable vue/require-v-for-key -->

<template>
  <div class="selection-canvas">
    <svg width="100%" height="1290" v-if="showSVG" :style="{position: 'absolute', }" 
    class="canvas" @click="onAddControlPoint($event)" @mousemove="onMovingControlPoint($event)">
      <g>
        <polygon :points="polygonPoints" fill="transparent" stroke="#fff" stroke-width="1" />
        <circle v-for="(p, i) in shape" :cx="p[0]" :cy="p[1]" r="4" :key="i" fill="#fff" />
      </g>
    </svg>
    <!-- 这里尝试画一个圆 -->
    <div v-if="canDrawCircle" class="cirleCanvas" @mousedown="startDrawCircle($event)" @mousemove="drawCircle($event)" @mouseup="finishDrawCircle">
      <svg width="100%" height="1290" v-if="showSVG" :style="{position: 'absolute'}">
        <g>
          <circle v-for="c in structureStore.structure"
          :cx="c.center[0]" :cy="c.center[1]" 
          r="20" fill="transparent" stroke="#fff" stroke-width="1"/>
        </g>
      </svg>
    </div>
    <div class="menu">
      <div class="btn-div" @click="onDrawing(c)" v-for="c in structureStore.structure" :key="c.name"> {{ c.name }} * {{
        c.nArray }} </div>
      <div class="btn-div" @click="onStartMonitor">
        START
      </div>
      <div class="btn-div" @click="openFilePicker">选择背景图片</div>
      <input class='file_input' type="file" accept="image/*" style="display: none;" @change="setBackgroundImage" />
    </div>
  </div>
</template>

<script lang="ts">
import { useStructureStore } from '../../stores/structure'
import { onMounted, ref, computed } from 'vue'
import { start } from 'repl'

export default {
  name: 'selection-canvas',
  setup() {
    const structureStore = useStructureStore()
    const shape = ref<[number, number][]>([])
    const componentNameDrawed = ref('')
    const showSVG = ref(false)
    const isDrawing = ref(false)

    //画圆的外形属性
    const isDrawCircle = ref(false);
    const center = ref<[number, number]>([0, 0]);
    const radius = ref(0);
    const canDrawCircle = ref(false);

    //画圆的函数
    const startDrawCircle = (e: MouseEvent) => {
      console.log("startDrawCircle");
      center.value = [e.pageX, e.pageY];
    };

    const drawCircle = (e: MouseEvent) => {
        radius.value = Math.sqrt( Math.pow(e.pageX - center.value[0], 2) + Math.pow(e.pageY- center.value[1], 2));
    };
 
    const finishDrawCircle = () => {
      if (isDrawCircle.value) {
        isDrawCircle.value = false;
        structureStore.setCircle(center.value, radius.value,componentNameDrawed.value);
      }
    };

    const polygonPoints = computed(() => {
      return shape.value.map(point => `${point[0]},${point[1]}`).join(' ')
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
      if (isDrawing.value) {
        shape.value[shape.value.length - 1] = [e.pageX, e.pageY]
      }
    }

    const onAddControlPoint = (e: MouseEvent) => {
      if (isDrawing.value) {
        shape.value.push([e.pageX, e.pageY])
      }
      if (componentNameDrawed.value && !isDrawing.value) {
        shape.value = [[e.pageX, e.pageY], [e.pageX, e.pageY]]
        isDrawing.value = true
      }
    }

    const finishDrawing = () => {
      shape.value = shape.value.slice(0, shape.value.length - 1)
      if (shape.value.length >= 3) {
        structureStore.setShape(shape.value, componentNameDrawed.value)
      }
      componentNameDrawed.value = ''
      isDrawing.value = false
      showSVG.value = false
      shape.value = []
    }

    const onStartMonitor = () => {
      // structureStore.startMonitor()
      structureStore.getdata()
    }

    const openFilePicker = () => {
      const file_input_btn = document.querySelector('.file_input') as HTMLElement;
      file_input_btn.click()
    };

    const setBackgroundImage = (event: Event) => {
      const inputElement = event.target as HTMLInputElement;
      if (inputElement.files && inputElement.files.length > 0) {
        const file = inputElement.files[0];
        const reader = new FileReader();

        reader.onload = () => {
          const imageUrl = reader.result as string;
          const explorationElement = document.querySelector('.exploration') as HTMLElement;
          explorationElement.style.backgroundImage = `url(${imageUrl})`;
        };

        reader.readAsDataURL(file);
      }
    };

    onMounted(() => {
      document.addEventListener("keydown", (e) => {
        if (e.code === 'Space' && isDrawing.value) {
          finishDrawing()
        }
        if (e.code === 'ControlLeft') {
          canDrawCircle.value = true;
          isDrawing.value = false;
        }
      })
     } 
    )

    return {
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
      startDrawCircle,
      drawCircle,
      finishDrawCircle,
      center,
      radius,
      canDrawCircle,
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
    background-color: #191D88;
    color: #191D88;

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
