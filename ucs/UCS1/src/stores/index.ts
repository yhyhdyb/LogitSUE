// store/index.js
import { createStore } from 'vuex';

export default createStore({
  state: {
    mapIndex:0,
  },
  mutations: {
    setSharedValue(state, newValue) {
      state.mapIndex = newValue;
    },
  },
  actions: {
    updateSharedValue({ commit }, newValue) {
      commit('setSharedValue', newValue);
    },
  },
  getters: {
    getSharedValue: state => state.mapIndex,
  },
});
