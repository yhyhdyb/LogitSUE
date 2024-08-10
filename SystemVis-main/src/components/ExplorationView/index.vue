<template>
  <div class="exploration">
    <div class="background-image" id="background-image"></div>
    <div class="background-image" id="black"></div>
    <MyComponent
      v-for="c in structureStore.flattenStructures"
      :key="c.name"
      msg="you are a component"
      :component="c"
      :data="structureStore.data"
      v-show="c.drew"
    />
    <SelectionCanvas />
    <FilterView />
  </div>
</template>

<script lang="ts">
import { useStructureStore } from '../../stores/structure'
import { onMounted, ref } from 'vue'
import MyComponent from './MyComponent.vue'
import SelectionCanvas from './SelectionCanvas.vue'
import FilterView from './FilterView.vue'
export default {
  name: 'demo-dd',
  components: {
    MyComponent,
    SelectionCanvas,
    FilterView,
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

  .background-image {
    position: absolute;
    top: 50px;
    left: 0px;
    height: calc(100% - 50px);
    width: 100%;
    background-size: contain;
    background-repeat: no-repeat;
  }
}
</style>
