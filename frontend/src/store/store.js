import Vue from "vue";
import Vuex from "vuex";
import net from "@/store/modules/net";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    graph: {},
    graphData: {},
    graphStats: {
      graphData: undefined,
      graphStatsOrder: {
        vul: [
          "vul_count",
          "affected_asset",
          "affected_app",
          "affected_os",
          "affected_hw",
        ],
        asset: [
          "asset_count",
          "family_cnt",
          "app_family",
          "app_count",
          "os_family",
          "os_count",
          "hw_family",
          "hw_count",
        ],
        exploit: ["exploit_count"],
      },
      graphStats: {
        vul: {
          vul_count: -1,
          affected_asset: -1,
          affected_app: -1,
          affected_os: -1,
          affected_hw: -1,
        },
        asset: {
          asset_count: -1,
          family_cnt: -1,
          app_family: -1,
          app_count: -1,
          os_family: -1,
          os_count: -1,
          hw_family: -1,
          hw_count: -1,
        },
        exploit: {
          exploit_count: -1,
        },
      },
    },
    // graphStats: new Map([
    //   [
    //     "vul",
    //     new Map([
    //       ["vul_count", -1],
    //       ["affected_asset", -1],
    //       ["affected_app", -1],
    //       ["affected_os", -1],
    //       ["affected_hw", -1],
    //     ]),
    //   ],
    //   [
    //     "asset",
    //     new Map([
    //       ["asset_count", -1],
    //       ["family_cnt", -1],
    //       ["app_family", -1],
    //       ["app_count", -1],
    //       ["os_family", -1],
    //       ["os_count", -1],
    //       ["hw_family", -1],
    //       ["hw_count", -1],
    //     ]),
    //   ],
    //   ["exploit", new Map([["exploit_count", -1]])],
    // ]),
    translation: {
      graph_overview: "图谱概览",
      vul: "漏洞",
      asset: "全部资产",
      exploit: "漏洞利用（攻击）",
      "1vul": "漏洞",
      "2asset": "全部资产",
      "3exploit": "漏洞利用（攻击）",
      vul_count: "漏洞总计：",
      affected_asset: "受影响资产：",
      affected_app: "受影响应用程序：",
      affected_os: "受影响操作系统：",
      affected_hw: "受影响硬件：",
      asset_count: "资产总计：",
      family_cnt: "资产家族：",
      app_family: "应用程序家族：",
      os_family: "操作系统家族：",
      hw_family: "硬件家族：",
      app_count: "应用程序：",
      os_count: "操作系统：",
      hw_count: "硬件：",
      exploit_count: "利用总计：",
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
      console.log(data);
      // state.graphStats["vul"] = data["vul"];
      // state.graphStats["asset"] = data["asset"];
      // state.graphStats["exploit"] = data["exploit"];
      state.graphStats = data;
    },
  },
  actions: {},
  modules: { net: net },
});
