<template>
  <v-app>
    <v-system-bar app></v-system-bar>

    <v-navigation-drawer app>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-h6">
            <!--            Vulnerability<br />Knowledge Graph-->
            漏洞知识图谱<br />Vul-KG
          </v-list-item-title>
          <!--          <v-list-item-subtitle>Visualization System</v-list-item-subtitle>-->
          <v-list-item-subtitle>可视化系统</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item v-for="item in items" :key="item.title" :to="item.route">
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: "App",

  data: () => ({
    items: [
      { title: "控制台", icon: "mdi-view-dashboard", route: "/dashboard" },
      { title: "搜索", icon: "mdi-database-search", route: "/search" },
      { title: "关于", icon: "mdi-information", route: "/about" },
    ],
    right: null,
  }),
  mounted() {
    // this.$store.dispatch("fetchGraphData", 20);
  },
};
</script>
