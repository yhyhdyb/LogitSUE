<template>
  <div class="filter-view">
    <div class="component" v-for="c in tree" :key="c.name">
      <div class="component-name">
        {{ c.name }}
      </div>
      <div class="sensor" v-for="s in c.sensors" :key="s">
        <el-checkbox fill="#000" @change="valueChange($event, s)" checked="true" :label="s" />
      </div>
    </div>
    <div class="btn" @click="filterSensors">FILTER</div>
  </div>
</template>

<script lang="ts">
import { useStructureStore } from '../../stores/structure'
import { onMounted, ref, computed } from 'vue'
import { flatten } from 'lodash'

export default {
  name: 'filter-view',
  setup() {
    const structureStore = useStructureStore()
    const tree = computed(() => {
      return structureStore.structure.map((c) => {
        return {
          name: c.name,
          sensors: flatten(c.sensorGroups[0].groups),
        }
      })
    })

    const sensorsChecked = computed(() => {
      const sensorsChecked: { [name: string]: boolean } = {}
      tree.value.forEach((c) => {
        c.sensors.forEach((s) => {
          sensorsChecked[s] = true
        })
      })
      return sensorsChecked
    })

    const removed: { [s: string]: boolean } = {}

    const valueChange = (e: MouseEvent, s: string) => {
      if (!e) {
        removed[s] = true
      } else {
        delete removed[s]
      }
    }

    const filterSensors = () => {
      structureStore.filterSensors(removed)
      structureStore.reLayoutTotally()
    }

    onMounted(() => {
      structureStore.filterSensors(removed)
    })

    return {
      filterSensors,
      valueChange,
      tree,
      sensorsChecked,
    }
  },
}
</script>
<style scoped lang="scss">
.filter-view {
  position: absolute;
  right: 0;
  top: 50px;
  width: 400px;
  height: calc(100% - 50px);
  background-color: rgba($color: #e1e9f2, $alpha: 0.9);
  border-left: 1px;
  overflow: scroll;

  .btn {
    top: 0px;
    position: absolute;
    left: calc(100% - 150px);
    width: 140px;
    height: 30px;
    margin: 10px;
    background-color: #fff;
    text-align: center;
    line-height: 30px;
    font-weight: 400;
    user-select: none;
    float: left;
    color: #4f709c;
    border: 1px solid #213555;
  }

  .btn:hover {
    font-weight: 600;
  }

  .component {
    position: relative;
    width: 100%;
    margin-top: 20px;

    .component-name {
      position: relative;
      width: 100%;
      height: 30px;
      font-weight: 600;
      font-size: 20px;
      line-height: 30px;
      padding-left: 10px;
    }

    .sensor {
      position: relative;
      width: 100%;
      height: 20px;
      font-weight: 400;
      font-size: 12px;
      line-height: 20px;
      padding-left: 30px;
    }
  }
}
/* custom scrollbar */
::-webkit-scrollbar {
  width: 20px;
}

::-webkit-scrollbar-track {
  background-color: transparent;
}

::-webkit-scrollbar-thumb {
  background-color: #213555;
  border-radius: 20px;
  border: 6px solid transparent;
  background-clip: content-box;
}
</style>
