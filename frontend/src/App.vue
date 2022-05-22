<template>
  <v-app>
    <v-system-bar app class="text-caption" color="grey lighten-3">
      <v-row no-gutters class="align-center px-2 flex-nowrap d-flex">
        <v-row no-gutters class="appBarFloatLeft">
          <v-col>
            <span>数据更新：{{ lastUpdate.format("L") }}</span>
          </v-col>
        </v-row>
        <v-spacer></v-spacer>
        <v-col class="text-center">
          <span>{{ datetime.format("llll") }}</span>
        </v-col>
        <v-spacer></v-spacer>
        <v-row no-gutters class="appBarFloatRight">
          <v-col class="mr-2 text-right shrink" style="white-space: nowrap">
            <span>当前用户：{{ username }}</span>
          </v-col>
          <v-col class="text-right shrink" style="white-space: nowrap">
            <span v-if="!isLoggedIn" class="blue--text">登录</span>
            <span v-if="isLoggedIn" class="blue--text">登出</span>
          </v-col>
        </v-row>
      </v-row>
    </v-system-bar>

    <v-navigation-drawer app>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-h6">
            <!--            Vulnerability<br />Knowledge Graph-->
            漏洞知识图谱<br />VulKG
          </v-list-item-title>
          <!--          <v-list-item-subtitle>Visualization System</v-list-item-subtitle>-->
          <v-list-item-subtitle>可视化系统</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item
          v-for="item in items"
          :key="item.title"
          :to="item.route"
          color="primary"
        >
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title class="body-1">{{
              item.title
            }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid class="ma-0 pa-0">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { mapState } from "vuex";
import moment from "moment";
export default {
  name: "App",

  data: () => ({
    items: [
      { title: "概览", icon: "mdi-view-dashboard", route: "/overview" },
      { title: "可视化", icon: "mdi-graphql", route: "/vis" },
      { title: "搜索", icon: "mdi-database-search", route: "/search" },
      { title: "控制台", icon: "mdi-cog", route: "/dashboard" },
      { title: "关于", icon: "mdi-information", route: "/about" },
    ],
    right: null,
    timer: undefined,
  }),
  computed: {
    ...mapState({
      username: (state) => state.username,
      mmt: (state) => state.mmt,
      datetime: (state) => state.datetime,
      lastUpdate: (state) => state.lastUpdate,
      isLoggedIn: (state) => state.isLoggedIn,
    }),
  },
  mounted() {
    // this.$store.dispatch("fetchGraphData", 20);
    this.mmt.locale("zh-cn");
    this.mmt.defaultFormat = "L";
    this.$store.commit("setDatetime");
    this.$store.commit("setLastUpdate", this.mmt());
    this.timer = setInterval(() => {
      this.$store.commit("setDatetime");
    }, 1000);
  },
};
</script>
<style src="./styles/base.css" scoped></style>
<style>
.vis-graph {
  width: 100%;
  height: 100%;
}
.content-container {
  max-width: 800px;
  min-height: 95vh;
}
.appBarFloatRight {
  position: absolute;
  right: 16px;
}
.appBarFloatLeft {
  position: absolute;
  left: 16px;
}
</style>
