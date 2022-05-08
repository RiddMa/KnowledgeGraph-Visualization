<template>
  <v-container fluid id="graph-container" class="ma-0" style="height: 95vh">
    <v-row>
      <v-col>
        <!--        <h1>Knowledge Graph Overview</h1>-->
        <h1>{{ translation.graph_overview }}</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <!--              <h2>Vulnerability</h2>-->
              <h2>{{ translation.vul }}</h2>
            </v-col>
          </v-row>
          <entry-list :entry-translate="translation" :vul-stats="vulStats" />
        </v-card>
      </v-col>
      <v-col>
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <!--              <h2>Asset</h2>-->
              <h2>{{ translation.asset }}</h2>
            </v-col>
          </v-row>
          <entry-list :entry-translate="translation" :vul-stats="assetStats" />
        </v-card>
      </v-col>
      <v-col>
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <!--              <h2>Exploit</h2>-->
              <h2>{{ translation.exploit }}</h2>
            </v-col>
          </v-row>
          <entry-list
            :entry-translate="translation"
            :vul-stats="exploitStats"
          />
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <h2>{{ translation.threat_info }}</h2>
            </v-col>
          </v-row>
          <v-row>
            <v-col> 排行</v-col>
            <v-col> 图示</v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <h2>{{ translation.latest_vul }}</h2>
            </v-col>
          </v-row>
          <v-row>
            <v-col> 排行</v-col>
          </v-row>
        </v-card>
      </v-col>
      <v-col>
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <h2>{{ translation.latest_exploit }}</h2>
            </v-col>
          </v-row>
          <v-row>
            <v-col> 列表</v-col>
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
import EntryList from "@/components/EntryList";

export default {
  name: "Dashboard",
  components: { EntryList },
  data: () => ({}),
  computed: {
    ...mapState({
      translation: (state) => state.translation,
      graphStats: (state) => state.graphStats,
      graphData: (state) => state.graphData,
      vulStats: (state) =>
        (({ vul_count }) => ({ vul_count }))(state.graphStats),
      assetStats: (state) =>
        (({ asset_count, app_count, os_count, hw_count }) => ({
          asset_count,
          app_count,
          os_count,
          hw_count,
        }))(state.graphStats),
      exploitStats: (state) =>
        (({ exploit_count }) => ({ exploit_count }))(state.graphStats),
    }),
  },
  async mounted() {
    await this.$store.dispatch("fetchGraphStats");
    // if (this.graphData === undefined) {
    //   await this.$store.dispatch("fetchGraphData", 20);
    // }
    // draw2DGraph(this.graphData);
  },
};
</script>
