<script setup lang="ts">
import '@/assets/historgram_content.css'
import { useNetworksData } from '@/stores/networkData'
import { computed } from 'vue'

interface rgbColorObj {
  r: number
  g: number
  b: number
  a: number
}

// 将值转换为颜色
function rgb_color_obj_transition(std_val: number, colors_transition: rgbColorObj[]) {
  let color_domain_idx = 0

  // 判断颜色区间
  const domain_size = colors_transition.length - 1
  for (let i = 1; i <= domain_size; i++) {
    if (std_val < i / domain_size) break
    else color_domain_idx += 1
  }
  if (color_domain_idx >= domain_size) color_domain_idx = domain_size - 1

  // 获取域内颜色
  let domain_std_val = (std_val - color_domain_idx / domain_size) * domain_size
  if (domain_std_val < 0) domain_std_val = 0
  else if (domain_std_val > 1) domain_std_val = 1

  const cid = color_domain_idx
  let color_projection = {
    r:
      colors_transition[cid].r +
      (colors_transition[cid + 1].r - colors_transition[cid].r) * domain_std_val,
    g:
      colors_transition[cid].g +
      (colors_transition[cid + 1].g - colors_transition[cid].g) * domain_std_val,
    b:
      colors_transition[cid].b +
      (colors_transition[cid + 1].b - colors_transition[cid].b) * domain_std_val,
    a:
      colors_transition[cid].a +
      (colors_transition[cid + 1].a - colors_transition[cid].a) * domain_std_val
  }

  return color_projection
}

//父组件传入子组件content_id
const props = defineProps({
  network_idx: {
    type: Number,
    default: 0
  },
  show_link_idx: {
    type: Number,
    default: 0
  }
})
const networkData = useNetworksData()
const compute_attr_shape = computed(() => {
  const tf_ratio_scope = networkData.historgram_data.graph_scope[6]
  const speed_scope = networkData.historgram_data.graph_scope[2]
  const network_link_idx =
    networkData.sel_links_networks_idx[props.network_idx][props.show_link_idx]
  if (network_link_idx == -1) {
    return {
      w: 0,
      h: 0
    }
  }
  const now_link = networkData.networksInfoArr[props.network_idx].links[network_link_idx]
  let flow_width = (100 * (now_link.flow / now_link.capacity)) / tf_ratio_scope[1]
  let tt_height = (100 * now_link.speed) / speed_scope[1]
  // console.log(now_link.flow, now_link.travelTime, now_link.speed, 'id:', now_link.globalId + 1)
  return {
    w: flow_width,
    h: tt_height
  }
})
const box_bgc = computed(() => {
  const network_link_idx =
    networkData.sel_links_networks_idx[props.network_idx][props.show_link_idx]
  if (network_link_idx == -1) {
    return 'rgba(255,255,255,0.3)'
  }
  const now_link = networkData.networksInfoArr[props.network_idx].links[network_link_idx]
  const now_sumcost = now_link.travelTime
  let std_now_sumcost =
    0.5 +
    (now_sumcost / networkData.global_links_init_sumcost[now_link.globalId] - 1) /
      networkData.matrix_element_radius /
      2
  if (networkData.matrix_element_radius == 0) std_now_sumcost = 0.5
  const box_bgc_transition_arr = [
    { r: 255, g: 130, b: 130, a: 0.3 },
    { r: 255, g: 255, b: 255, a: 0.3 },
    { r: 130, g: 255, b: 130, a: 0.3 }
  ] as rgbColorObj[]

  const now_bgc_obj = rgb_color_obj_transition(1 - std_now_sumcost, box_bgc_transition_arr)
  return (
    'rgba(' + now_bgc_obj.r + ',' + now_bgc_obj.g + ',' + now_bgc_obj.b + ',' + now_bgc_obj.a + ')'
  )
})

const if_unshow = computed(() => {
  const network_link_idx =
    networkData.sel_links_networks_idx[props.network_idx][props.show_link_idx]
  return {
    unshow: network_link_idx == -1
  }
})
</script>
<template>
  <div class="matrix_link_info_box" :class="if_unshow" :style="{ backgroundColor: box_bgc }">
    <div
      class="inherent_attr_rect"
      :style="{ width: 100 / networkData.historgram_data.graph_scope[6][1] + '%' }"
    ></div>
    <div
      class="compute_attr_rect"
      :style="{ width: compute_attr_shape.w + '%', height: compute_attr_shape.h + '%' }"
    ></div>
  </div>
</template>

<style scoped>
.matrix_link_info_box {
  width: 100%;
  height: 100%;
  position: relative;
  text-align: center;
  overflow: hidden;
}
.matrix_link_info_box .inherent_attr_rect,
.matrix_link_info_box .compute_attr_rect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  margin-left: auto;
  margin-right: auto;
}
.matrix_link_info_box .inherent_attr_rect {
  /* width: 60%; */
  height: 100%;
  background-color: #d3d2e2;
}
.matrix_link_info_box .compute_attr_rect {
  /* width: 70%;
    height: 50%; */
  background-color: #6362aeca;
}
.unshow {
  display: none;
}
</style>
