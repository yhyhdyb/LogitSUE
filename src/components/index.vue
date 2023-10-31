<!-- eslint-disable vue/require-v-for-key -->
<template>
  <div class="index-view">
    <g>
      <svg width="100%" height="100%">
        <circle
          v-for="n in nodes"
          :key="n.ID"
          :cx="mapX(n.PositionX)"
          :cy="mapY(n.PositionY)"
          r="15"
          fill="#FFFFFF"
          stroke="#000000"
        />
        <line
          v-for="pl in pairsLocation"
          :x1="mapX(pl[0][0])"
          :y1="mapY(pl[0][1])"
          :x2="mapX(pl[1][0])"
          :y2="mapY(pl[1][1])"
          stroke="green"
          stroke-width="5"
        />
      </svg>
    </g>
  </div>
</template>

<script lang="ts">
import { Link, node, useNetworkStore } from "../store/index";
import { onBeforeMount, ref } from "vue";
export default {
  name: "index-view",
  setup() {
    const networkStore = useNetworkStore();
    const nodes = ref([] as node[]);
    const links = ref([] as Link[]);
    const pairs = ref(Array<Array<number>>()); //存放路段的起点和终点ID
    const pairsLocation = ref(Array<Array<Array<number>>>()); //存放路段的起点和终点坐标[[x1,y1],[x2,y2]]
    // Fetch data when the component is about to mount
    onBeforeMount(async () => {
      await networkStore.fetchNodes();
      await networkStore.fetchLinks();
      await networkStore.fetchODPairs();
      await networkStore.fetchPaths();
      nodes.value = JSON.parse(JSON.stringify(networkStore.nodes));
      links.value = JSON.parse(JSON.stringify(networkStore.links.links));
      console.log("links =", links.value);
      //先获取路段的起点和终点ID
      for (let i = 0; i < links.value.length; i++) {
        console.log(links.value[i].pInNode, links.value[i].pOutNode);
        pairs.value.push([links.value[i].pInNode, links.value[i].pOutNode]);
      }

      //再获取路段的起点和终点坐标
      for (let i = 0; i < pairs.value.length; i++) {
        for (let j = 0; j < nodes.value.length; j++) {
          if (pairs.value[i][0] == nodes.value[j].ID) {
            pairsLocation.value.push([
              [nodes.value[j].PositionX, nodes.value[j].PositionY],
              [0, 0],
            ]);
          }
        }
      }
      for (let i = 0; i < pairs.value.length; i++) {
        for (let j = 0; j < nodes.value.length; j++) {
          if (pairs.value[i][1] == nodes.value[j].ID) {
            pairsLocation.value[i][1] = [
              nodes.value[j].PositionX,
              nodes.value[j].PositionY,
            ];
          }
        }
      }
      console.log("pairs =", pairs.value);
      console.log("pairsLocation =", pairsLocation.value);
      console.log("nodes =", nodes.value);
    });
    // const selectNode = (n: unknown) => {
    //   n.isSelected = !n.isSelected;
    //   console.log(n.isSelected);
    // };
    const mapX = (x: number) => {
      // map x coordinate to screen
      return x * 30;
    };
    const mapY = (y: number) => {
      // map y coordinate to screen
      return y * 30;
    };
    return {
      nodes,
      links,
      networkStore,
      pairsLocation,
      mapX,
      mapY,
      //selectNode,
    };
  },
};
</script>
<style>
.index-view {
  width: 100%;
  height: 100%;
  margin: 0;
}
</style>
