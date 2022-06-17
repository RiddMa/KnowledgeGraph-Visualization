import { getSampleData } from "@/api/graph.api";
import { dispatchJob, terminateJob } from "@/api/dashboard.api";

const dashboardStore = {
  state: {
    services: [
      { name: "数据采集服务", id: "data_collection", running: true },
      { name: "知识图谱构建服务", id: "build_kg", running: false },
    ],
  },
  getters: {},
  mutations: {
    setRunningTask(state, runningTask) {
      state.runningTask = runningTask;
    },
  },
  actions: {
    async dispatchJob(context, jobName) {
      try {
        const response = await dispatchJob(jobName);
        return response.data;
        // context.commit("setGraphData", response.data);
      } catch (e) {
        console.log(e);
      }
    },
    async terminateJob(context, jobName) {
      try {
        const response = await terminateJob(jobName);
        return response.data;
        // context.commit("setGraphData", response.data);
      } catch (e) {
        console.log(e);
      }
    },
  },
};
export default dashboardStore;
