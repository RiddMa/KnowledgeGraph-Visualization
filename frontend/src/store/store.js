import Vue from "vue";
import Vuex from "vuex";
import net from "@/store/modules/net";
import _, { range } from "lodash";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    graph: {},
    graphData: {},
    graphStatsOrder: {},
    // graphStats: {},
    graphStats: {
      vul: [
        { name: "vul_count", value: 0 },
        { name: "affected_asset", value: 0 },
        { name: "affected_app", value: 0 },
        { name: "affected_os", value: 0 },
        { name: "affected_hw", value: 0 },
      ],
      asset: [
        { name: "asset_count", value: 0 },
        { name: "family_cnt", value: 0 },
        { name: "app_family", value: 0 },
        { name: "app_count", value: 0 },
        { name: "os_family", value: 0 },
        { name: "os_count", value: 0 },
        { name: "hw_family", value: 0 },
        { name: "hw_count", value: 0 },
      ],
      exploit: [
        { name: "exploit_count", value: 0 },
        { name: "webapps", value: 0 },
        { name: "remote", value: 0 },
        { name: "local", value: 0 },
        { name: "dos", value: 0 },
      ],
    },
    translation: {
      graph_overview: "图谱概览",
      vul: "漏洞",
      asset: "全部资产",
      exploit: "漏洞利用（攻击）",
      "1vul": "漏洞",
      "2asset": "全部资产",
      "3exploit": "漏洞利用（攻击）",
      vul_count: "漏洞总计",
      affected_asset: "受影响资产",
      affected_app: "受影响应用程序",
      affected_os: "受影响操作系统",
      affected_hw: "受影响硬件",
      asset_count: "资产总计",
      family_cnt: "资产家族",
      app_family: "应用程序家族",
      os_family: "操作系统家族",
      hw_family: "硬件家族",
      app_count: "应用程序",
      os_count: "操作系统",
      hw_count: "硬件",
      exploit_count: "利用总计",
      webapps: "网页应用",
      remote: "远程",
      local: "本地",
      dos: "DOS",
      threat_info: "威胁情报",
      latest_vul: "最新漏洞",
      latest_exploit: "最新攻击",
    },
  },
  getters: {
    getGraphData(state) {
      return state.graphData;
    },
  },
  mutations: {
    setGraph(state, { name, graph }) {
      state.graph[name] = graph;
    },
    setGraphData(state, { name, data }) {
      state.graphData[name] = data;
    },
    setGraphStats(state, data) {
      state.graphStats = data;
    },
  },
  actions: {},
  modules: { net: net },
});
