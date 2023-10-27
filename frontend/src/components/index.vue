<template>
  <div>sb</div>
</template>
<script lang="ts">
import { useNetworkStore } from "../store/index";
export default {
  name: "index-view",
  components: {},

  setup() {
    const networkStore = useNetworkStore();
    networkStore.fetchNodes();
    networkStore.fetchLinks();
    networkStore.fetchODPairs();
    networkStore.fetchPaths();
    //console.log(JSON.stringify(networkStore.nodes));

    return {};
  },
};
</script>
