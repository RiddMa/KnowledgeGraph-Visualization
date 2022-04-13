<template>
  <v-app>
    <v-system-bar app> </v-system-bar>

    <v-navigation-drawer app>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-h6">
            Cyber Security<br />Knowledge Graph
          </v-list-item-title>
          <v-list-item-subtitle>Visualization</v-list-item-subtitle>
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
      { title: "Dashboard", icon: "mdi-view-dashboard", route: "/dashboard" },
      { title: "Search", icon: "mdi-database-search", route: "/search" },
      { title: "About", icon: "mdi-information", route: "/about" },
    ],
    right: null,
  }),
  mounted() {
    // this.$store.dispatch("fetchGraphData", 20);
  },
};
</script>
