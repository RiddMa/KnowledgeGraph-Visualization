<template>
  <v-container fluid id="graph-container" class="ma-0" style="height: 95vh">
    <v-row>
      <v-col>
        <h1>{{ translation.graph_overview }}</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" sm="12" md="6" lg="4">
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <h2>{{ translation["vul"] }}</h2>
            </v-col>
          </v-row>
          <entry-list
            :entry-translate="translation"
            :stats="this.graphStats.vul"
          />
          <!--          <v-row class="mt-2 mb-0 mx-0 pa-0">-->
          <!--            <v-col class="ma-0 pa-0">-->
          <stats-graph
            graph-id="stats-graph-vul"
            type="vul"
            :nodes="this.getVulChartData()"
            style="height: 260px"
          ></stats-graph>
          <!--            </v-col>-->
          <!--          </v-row>-->
        </v-card>
      </v-col>
      <v-col cols="12" sm="12" md="6" lg="4">
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <h2>{{ translation["asset"] }}</h2>
            </v-col>
          </v-row>
          <entry-list
            :entry-translate="translation"
            :stats="this.graphStats.asset"
          />
          <stats-graph
            graph-id="stats-graph-asset"
            type="asset"
            :nodes="this.getAssetFamilyChartData()"
            style="height: 260px"
          ></stats-graph>
        </v-card>
      </v-col>
      <v-col cols="12" sm="12" md="6" lg="4">
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <h2>{{ translation["exploit"] }}</h2>
            </v-col>
          </v-row>
          <entry-list
            :entry-translate="translation"
            :stats="this.graphStats.exploit"
          />
        </v-card>
      </v-col>
      <!--      <v-col sm="12" md="6" lg="4">-->
      <!--        <v-card class="pa-6">-->
      <!--          <v-row>-->
      <!--            <v-col>-->
      <!--              &lt;!&ndash;              <h2>Vulnerability</h2>&ndash;&gt;-->
      <!--              <h2>{{ translation.vul }}</h2>-->
      <!--            </v-col>-->
      <!--          </v-row>-->
      <!--          <entry-list :entry-translate="translation" :vul-stats="vulStats" />-->
      <!--        </v-card>-->
      <!--      </v-col>-->
      <!--      <v-col cols="12" sm="12" md="6" lg="4">-->
      <!--        <v-card class="pa-6">-->
      <!--          <v-row>-->
      <!--            <v-col>-->
      <!--              &lt;!&ndash;              <h2>Asset</h2>&ndash;&gt;-->
      <!--              <h2>{{ translation.asset }}</h2>-->
      <!--            </v-col>-->
      <!--          </v-row>-->
      <!--          <entry-list :entry-translate="translation" :vul-stats="assetStats" />-->
      <!--        </v-card>-->
      <!--      </v-col>-->
      <!--      <v-col cols="12" sm="12" md="6" lg="4">-->
      <!--        <v-card class="pa-6">-->
      <!--          <v-row>-->
      <!--            <v-col>-->
      <!--              &lt;!&ndash;              <h2>Exploit</h2>&ndash;&gt;-->
      <!--              <h2>{{ translation.exploit }}</h2>-->
      <!--            </v-col>-->
      <!--          </v-row>-->
      <!--          <entry-list-->
      <!--            :entry-translate="translation"-->
      <!--            :vul-stats="exploitStats"-->
      <!--          />-->
      <!--        </v-card>-->
      <!--      </v-col>-->
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
import _, { range } from "lodash";
import { mapState } from "vuex";
import EntryList from "@/components/EntryList";
import StatsGraph from "@/components/StatsGraph";

export default {
  name: "Dashboard",
  components: { StatsGraph, EntryList },
  data: () => ({}),
  computed: {
    ...mapState({
      translation: (state) => state.translation,
      graphStats: (state) => state.graphStats,
      graphStatsOrder: (state) => state.graphStatsOrder,
      graphData: (state) => state.graphData,
      overviewStats: (state) => state.graphStats,
      // vulStats: (state) => state.graphStats.vul,
      // assetStats: (state) => state.graphStats.asset,
      // exploitStats: (state) => state.graphStats.exploit,
    }),
  },
  methods: {
    getVulChartData() {
      let arr = _.cloneDeep(this.graphStats.vul);
      arr = arr.slice(2, arr.length);
      for (const i in range(0, arr.length)) {
        let translatedName = this.translation[arr[i]["name"]];
        arr[i]["name"] = translatedName.substring(3, translatedName.length - 1);
      }

      let total = 0;
      for (const i of range(0, arr.length)) {
        total += arr[i]["value"];
      }
      for (const i of range(0, arr.length)) {
        arr[i]["percentage"] = arr[i]["value"] / total;
      }
      return arr;
    },
    getAssetChartData() {
      let arr = _.cloneDeep(this.graphStats.asset);
      arr = arr.slice(2, arr.length);
      for (const i in range(0, arr.length)) {
        let translatedName = this.translation[arr[i]["name"]];
        arr[i]["name"] = translatedName.substring(0, translatedName.length - 1);
      }
      arr = [arr[1], arr[3], arr[5]];
      console.log(arr);
      return arr;
    },
    getAssetFamilyChartData() {
      let arr = _.cloneDeep(this.graphStats.asset);
      arr = arr.slice(2, arr.length);
      for (const i in range(0, arr.length)) {
        let translatedName = this.translation[arr[i]["name"]];
        arr[i]["name"] = translatedName.substring(0, translatedName.length - 1);
      }
      arr = [arr[0], arr[2], arr[4]];
      console.log(arr);
      return arr;
    },
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
