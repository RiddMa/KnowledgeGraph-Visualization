import Vue from "vue";
import Vuex from "vuex";
import net from "@/store/modules/net";
Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    graphData: undefined,
    graphStats: {
      vuln_count: -1,
      asset_count: -1,
      atk_count: -1,
      os_count: -1,
      app_count: -1,
      hw_count: -1,
    },
  },
  getters: {
    getGraphData(state) {
      return state.graphData;
    },
  },
  mutations: {
    setGraphData(state, data) {
      state.graphData = data;
    },
    setGraphStats(state, data) {
      state.graphStats = data;
    },
  },
  actions: {},
  modules: { net: net },
});
