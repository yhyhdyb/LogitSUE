<template>
  <div class="exploration">
    <MyComponent v-for="c in structureStore.flattenStructures" :key="c.name" msg="you are a component" :component="c"
      :data="structureStore.data" v-show="c.drew" />
    <SelectionCanvas />
  </div>
</template>

<script lang="ts">
import { useStructureStore } from '../../stores/structure'
import { onMounted, ref } from 'vue'
import MyComponent from './MyComponent.vue'
import SelectionCanvas from './SelectionCanvas.vue'
export default {
  name: 'demo-dd',
  components: {
    MyComponent,
    SelectionCanvas,
  },

  setup() {
    const structureStore = useStructureStore()

    // onMounted(() => {
    //   structureStore.getdata()
    // })

    return {
      structureStore,
    }
  },
}
</script>
<style scoped lang="scss">
.exploration {
  position: relative;
  height: 100%;
  width: 100%;
}
</style>
