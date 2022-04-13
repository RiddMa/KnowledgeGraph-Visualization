import { getGraphData, getGraphSearch, getGraphStats } from "@/api/base.api";
const net = {
  state: {},
  getters: {},
  mutations: {},
  actions: {
    async fetchGraphData(context, limit) {
      try {
        const response = await getGraphData(limit);
        context.commit("setGraphData", response.data);
      } catch (e) {
        console.log(e);
      }
    },
    async fetchGraphStats(context) {
      try {
        const response = await getGraphStats();
        context.commit("setGraphStats", response.data);
      } catch (e) {
        console.log(e);
      }
    },
    async fetchGraphSearch(context, keyword) {
      try {
        const response = await getGraphSearch(keyword);
        context.commit("setGraphData", response.data);
      } catch (e) {
        console.log(e);
      }
    },
  },
};
export default net;
