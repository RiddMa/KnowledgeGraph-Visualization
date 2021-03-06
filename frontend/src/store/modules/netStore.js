import {
  getGraphData,
  getGraphSearch,
  getGraphStats,
  getSampleData,
} from "@/api/graph.api";
import { sendHeartBeat } from "@/api/base.api";
const netStore = {
  state: {},
  getters: {},
  mutations: {},
  actions: {
    async fetchGraphData(context, { name: name, limit: limit }) {
      try {
        const response = await getGraphData(limit);
        context.commit("setGraphData", { name: name, data: response.data });
        return response.data;
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
    async fetchGraphSearch(context, { name: name, keyword: keyword }) {
      try {
        const response = await getGraphSearch(keyword);
        context.commit("setGraphData", { name: name, data: response.data });
        return response.data;
      } catch (e) {
        console.log(e);
      }
    },
    async getSampleData(context, url) {
      try {
        const response = await getSampleData(url);
        return response.data;
        // context.commit("setGraphData", response.data);
      } catch (e) {
        console.log(e);
      }
    },
    async sendHeartbeat(context) {
      try {
        const response = await sendHeartBeat();
        return response.data;
        // context.commit("setGraphData", response.data);
      } catch (e) {
        console.log(e);
      }
    },
  },
};
export default netStore;
