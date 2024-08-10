<template>
  <div class="exploration">
    <MyComponent
      v-for="c in structureStore.structure"
      :key="c.name"
      msg="you are a component"
      :component="c"
    />
  </div>
</template>

<script lang="ts">
import { useStructureStore } from '../../stores/structure'
import { onMounted } from 'vue'
import MyComponent from './MyComponent.vue'
export default {
  components: {
    MyComponent,
  },
  name: 'demo-dd',
  setup() {
    const structureStore = useStructureStore()

    onMounted(() => {})

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
