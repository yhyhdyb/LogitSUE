<script setup lang="ts">
// defineProps<{
//   msg: string
// }>()
import {ref, computed, onMounted} from 'vue'
const zoom_rat = ref(100)
const svg_box_width = ref(500)
const svg_box_height = ref(500)
const svg_x = ref(svg_box_width.value/2)
const svg_y = ref(svg_box_height.value/2)
const svg_width = ref(300)
const svg_height = ref(200)
// const mouse_push = ref(false)

// 计算属性
const svg_left = computed(() => {
  return svg_x.value-svg_width.value/2
})
const svg_top = computed(() => {
  return svg_y.value-svg_height.value/2
})

// 监听屏幕大小变化
function observeContainerSizeChanges(container: HTMLElement,
    callback: (width: number, height: number) => void) {
  const resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
      const { width, height } = entry.contentRect;
      callback(width, height);
    }
  });

  resizeObserver.observe(container);
}

function handle_mouse_move(event: MouseEvent) {
  if (event.buttons == 1) {
    // 鼠标左键被按下
    // 当右键被按下时为0
    // console.log(event);
    // 获取鼠标移动的偏移量
    const offsetX = event.movementX;
    const offsetY = event.movementY;

    // 处理鼠标移动的偏移量
    let svg_x_move = svg_x.value + offsetX
    let svg_zoom_rate = zoom_rat.value/100
    
    // 当svg内容是否超出盒子大小，处理方式相反
    if (svg_width.value*svg_zoom_rate < svg_box_width.value) {
      if (svg_x_move + svg_width.value/2*svg_zoom_rate > svg_box_width.value) {
        svg_x_move = svg_box_width.value - svg_width.value/2*svg_zoom_rate
      } else if (svg_x_move - svg_width.value*svg_zoom_rate/2 < 0) 
        svg_x_move = svg_width.value/2*svg_zoom_rate
    } else {
      if (svg_x_move + svg_width.value/2*svg_zoom_rate <= svg_box_width.value) {
        svg_x_move = svg_box_width.value - svg_width.value/2*svg_zoom_rate
      } else if (svg_x_move - svg_width.value*svg_zoom_rate/2 >= 0) 
        svg_x_move = svg_width.value/2*svg_zoom_rate
    }
    
    let svg_y_move = svg_y.value + offsetY
    if (svg_height.value*svg_zoom_rate < svg_box_height.value) {
      if (svg_y_move + svg_height.value/2*svg_zoom_rate > svg_box_height.value) {
        svg_y_move = svg_box_height.value - svg_height.value/2*svg_zoom_rate
      } else if (svg_y_move - svg_height.value*svg_zoom_rate/2 < 0) 
        svg_y_move = svg_height.value/2*svg_zoom_rate
    } else {
      if (svg_y_move + svg_height.value/2*svg_zoom_rate <= svg_box_height.value) {
        svg_y_move = svg_box_height.value - svg_height.value/2*svg_zoom_rate
      } else if (svg_y_move - svg_height.value*svg_zoom_rate/2 >= 0) 
        svg_y_move = svg_height.value/2*svg_zoom_rate
    }
    svg_x.value = svg_x_move
    svg_y.value = svg_y_move
    // svg_x.value += (offsetX)
    // svg_y.value += (offsetY)
    // console.log('X偏移量:', offsetX);
    // console.log('Y偏移量:', offsetY);
    // console.log(event);
    
  }
  // console.log(event);
}

function handle_wheel(event:WheelEvent) {
  console.log(event);
  const deltaX = event.deltaX;
  const deltaY = event.deltaY;
  if (deltaY > 0 && zoom_rat.value >= 20) {
    zoom_rat.value -= 10
  } else if (deltaY < 0) {
    zoom_rat.value += 10
  }
}

onMounted(() => {
  // 记录窗口大小
  const svg_box_target = document.getElementById("svg_box") as HTMLDivElement
  observeContainerSizeChanges(svg_box_target, (width, height) => {
    svg_box_height.value = height
    svg_box_width.value = width
  })
})
</script>

<template>
  <div class="network_show">
    <div class="network_box" id="svg_box">
      <svg version="1.1" 
        baseProfile="full"
        :width="svg_width" :height="svg_height"
        xmlns="http://www.w3.org/2000/svg"
        :style="{ transform: `scale(${zoom_rat/100})`, left: svg_left, top: svg_top}"
        @mousemove="handle_mouse_move($event)"
        @wheel.stop="handle_wheel($event)"
        id="map_svg">
        <rect width="100%" height="100%" stroke="red" stroke-width="4" fill="yellow" />
        <circle cx="150" cy="100" r="80" fill="green" />
        <text x="150" y="115" font-size="16" text-anchor="middle" fill="white">RUNOOB SVG TEST</text>
      </svg>
    </div>
    <label for="zoom"></label>
    <input type="number" name="zoom" id="" v-model="zoom_rat">
    <label for="left"></label>
    <input type="number" name="left" id="" v-model="svg_x">
    <label for="top"></label>
    <input type="number" name="top" id="" v-model="svg_y">
  </div>
</template>

<style scoped>
.network_show {
  /* width: 500px; */
  /* height: 500px; */
  background-color: antiquewhite;
}

#map_svg {
  /* width: 300px; */
  /* height: 400px; */
  position: absolute;
  z-index: 0;
  overflow: hidden;
}
.network_box {
  width: 500px;
  height: 500px;
  border: 1px solid black;
  position: relative;
  overflow: hidden;
  /* background-color: salmon; */
  z-index: 2;
}
</style>
