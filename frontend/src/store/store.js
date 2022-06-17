import Vue from "vue";
import Vuex from "vuex";
import netStore from "@/store/modules/netStore";
import viewStore from "@/store/modules/viewStore";
import moment from "moment";
import graphStore from "@/store/modules/graphStore";
import dashboardStore from "@/store/modules/dashboardStore";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    username: "未登录",
    isLoggedIn: false,
    mmt: moment,
    datetime: moment(),
    lastUpdate: moment(),
  },
  getters: {},
  mutations: {
    setDatetime(state) {
      state.datetime = state.mmt();
    },
    setLastUpdate(state, datetime) {
      state.lastUpdate = datetime;
    },
  },
  actions: {},
  modules: {
    netStore: netStore,
    viewStore: viewStore,
    graphStore: graphStore,
    dashboardStore: dashboardStore,
  },
});
