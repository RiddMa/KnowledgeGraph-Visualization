<template>
  <v-container fluid id="graph-container" class="ma-0" style="height: 95vh">
    <v-row>
      <v-col>
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <h2>Vulnerability</h2>
            </v-col>
          </v-row>
          <v-row>
            <v-col> Total: </v-col>
            <v-col>
              {{ graphStats.vuln_count }}
            </v-col>
          </v-row>
        </v-card>
      </v-col>
      <v-col>
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <h2>Asset</h2>
            </v-col>
          </v-row>
          <v-row>
            <v-col> Total: </v-col>
            <v-col>
              {{ graphStats.asset_count }}
            </v-col>
          </v-row>
          <v-row>
            <v-col> OS: </v-col>
            <v-col>
              {{ graphStats.os_count }}
            </v-col>
          </v-row>
          <v-row>
            <v-col> Application: </v-col>
            <v-col>
              {{ graphStats.app_count }}
            </v-col>
          </v-row>
          <v-row>
            <v-col> Hardware: </v-col>
            <v-col>
              {{ graphStats.hw_count }}
            </v-col>
          </v-row>
        </v-card>
      </v-col>
      <v-col>
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <h2>Attack</h2>
            </v-col>
          </v-row>
          <v-row>
            <v-col> Total: </v-col>
            <v-col>
              {{ graphStats.atk_count }}
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <div id="2d-graph"></div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapState } from "vuex";
import { draw2DGraph } from "@/utils/graph";

export default {
  name: "Dashboard",
  computed: {
    ...mapState({
      graphStats: (state) => state.graphStats,
      graphData: (state) => state.graphData,
    }),
  },
  async mounted() {
    await this.$store.dispatch("fetchGraphStats");
    if (this.graphData === undefined) {
      await this.$store.dispatch("fetchGraphData", 20);
    }
    draw2DGraph(this.graphData);
  },
};
</script>

<style scoped></style>
