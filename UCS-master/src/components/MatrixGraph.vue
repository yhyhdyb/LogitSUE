<script setup lang="ts">
import "@/assets/historgram_content.css"
import { useNetworksData } from '@/stores/networkData';
import { computed } from 'vue';

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
  const network_link_idx = networkData.sel_links_networks_idx[props.network_idx][props.show_link_idx]
  if (network_link_idx == -1) {
    return {
      w: 0,
      h: 0
    }
  }
  const now_link = networkData.networksInfoArr[props.network_idx].links[network_link_idx]
  let flow_width = 100*(now_link.flow/now_link.capacity)/tf_ratio_scope[1]
  let tt_height = 100*(now_link.speed)/speed_scope[1]
  return {
    w: flow_width,
    h: tt_height
  }
})
const if_unshow = computed(() => {
  const network_link_idx = networkData.sel_links_networks_idx[props.network_idx][props.show_link_idx]
  return {
    unshow: network_link_idx==-1
  }
})
</script>
<template>
  <div class="matrix_link_info_box" :class="if_unshow">
    <div class="inherent_attr_rect" :style="{width: 100/networkData.historgram_data.graph_scope[6][1]+'%'}"></div>
    <div class="compute_attr_rect"
      :style="{width: compute_attr_shape.w+'%', height: compute_attr_shape.h+'%'}"></div>
  </div>
</template>

<style scoped>
.matrix_link_info_box {
    width: 100%;
    height: 100%;
    position: relative;
    text-align: center;
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
    background-color: #D3D2E2;
}
.matrix_link_info_box .compute_attr_rect {
    /* width: 70%;
    height: 50%; */
    background-color: #6362AECA;
}
.unshow {
  display: none;
}
</style>