<template>
  <v-container fluid id="graph-container" class="content-container-wide">
    <v-row class="px-6 pt-6 mb-0 pb-0">
      <v-col>
        <p class="text-h3 ma-0">{{ translation.graph_overview }}</p>
      </v-col>
    </v-row>

    <v-row class="mt-0 pt-0">
      <v-col cols="12" sm="12" md="6" lg="4">
        <v-card class="pa-6" outlined raised>
          <v-row>
            <v-col>
              <p class="text-h4">{{ translation["vul"] }}</p>
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
            class="mt-4"
            style="height: 260px"
          ></stats-graph>
          <!--            </v-col>-->
          <!--          </v-row>-->
        </v-card>
      </v-col>
      <v-col cols="12" sm="12" md="6" lg="4">
        <v-card class="pa-6" outlined raised>
          <v-row>
            <v-col class="shrink" style="min-width: 180px">
              <p class="text-h4">{{ translation["asset"] }}</p>
            </v-col>
            <v-col class="ma-0 px-0">
              <v-btn-toggle dense v-model="assetChartToggle" mandatory>
                <v-btn>显示家族</v-btn>
                <v-btn>显示资产</v-btn>
              </v-btn-toggle>
            </v-col>
          </v-row>
          <entry-list
            :entry-translate="translation"
            :stats="this.graphStats.asset"
          />
          <stats-graph
            graph-id="stats-graph-asset-family"
            type="asset"
            :nodes="this.selectAssetChartData()"
            class="mt-4"
            style="height: 260px"
          ></stats-graph>
        </v-card>
      </v-col>
      <v-col cols="12" sm="12" md="6" lg="4">
        <v-card class="pa-6" outlined raised>
          <v-row>
            <v-col>
              <p class="text-h4">{{ translation["exploit"] }}</p>
            </v-col>
          </v-row>
          <entry-list
            :entry-translate="translation"
            :stats="this.graphStats.exploit"
          />
          <stats-graph
            graph-id="stats-graph-exploit"
            type="asset"
            :nodes="this.getExploitChartData()"
            class="mt-4"
            style="height: 260px"
          ></stats-graph>
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
        <v-card class="pa-6" outlined raised>
          <v-row>
            <v-col>
              <p class="text-h4">{{ translation.threat_info }}</p>
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
        <v-card class="pa-6" outlined raised>
          <v-row>
            <v-col>
              <p class="text-h4">{{ translation.latest_vul }}</p>
            </v-col>
          </v-row>
          <v-row>
            <v-col> 排行</v-col>
          </v-row>
        </v-card>
      </v-col>
      <v-col>
        <v-card class="pa-6" outlined raised>
          <v-row>
            <v-col>
              <p class="text-h4">{{ translation.latest_exploit }}</p>
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
  name: "Overview",
  components: { StatsGraph, EntryList },
  data: () => ({
    assetChartToggle: 0,
    showAssetFamily: true,
  }),
  computed: {
    ...mapState({
      translation: (state) => state.graphStore.translation,
      graphStats: (state) => state.graphStore.graphStats,
      graphStatsOrder: (state) => state.graphStore.graphStatsOrder,
      graphData: (state) => state.graphStore.graphData,
      overviewStats: (state) => state.graphStore.graphStats,
    }),
  },
  methods: {
    getVulChartData() {
      let arr = _.cloneDeep(this.graphStats.vul);
      arr = arr.slice(2, arr.length);
      for (const i in range(0, arr.length)) {
        let translatedName = this.translation[arr[i]["name"]];
        arr[i]["name"] = translatedName.substring(3, translatedName.length);
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
    selectAssetChartData() {
      if (this.assetChartToggle === 0) {
        return this.getAssetFamilyChartData();
      } else {
        return this.getAssetChartData();
      }
    },
    getAssetChartData() {
      let arr = _.cloneDeep(this.graphStats.asset);
      arr = arr.slice(2, arr.length);
      for (const i in range(0, arr.length)) {
        arr[i]["name"] = this.translation[arr[i]["name"]];
      }
      arr = _.cloneDeep([arr[1], arr[3], arr[5]]);
      let total = 0;
      for (const i of range(0, arr.length)) {
        total += arr[i]["value"];
      }
      for (const i of range(0, arr.length)) {
        arr[i]["percentage"] = arr[i]["value"] / total;
      }
      return arr;
    },
    getAssetFamilyChartData() {
      let arr = _.cloneDeep(this.graphStats.asset);
      arr = arr.slice(2, arr.length);
      for (const i in range(0, arr.length)) {
        arr[i]["name"] = this.translation[arr[i]["name"]];
      }
      arr = _.cloneDeep([arr[0], arr[2], arr[4]]);
      let total = 0;
      for (const i of range(0, arr.length)) {
        total += arr[i]["value"];
      }
      for (const i of range(0, arr.length)) {
        arr[i]["percentage"] = arr[i]["value"] / total;
      }
      return arr;
    },
    getExploitChartData() {
      let arr = _.cloneDeep(this.graphStats.exploit);
      arr = arr.slice(1, arr.length);
      for (const i in range(0, arr.length)) {
        arr[i]["name"] = this.translation[arr[i]["name"]];
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
  },
  mounted() {
    this.$store.dispatch("fetchGraphStats");
    // if (this.graphData === undefined) {
    //   await this.$store.dispatch("fetchGraphData", 20);
    // }
    // draw2DGraph(this.graphData);
  },
};
</script>
<style src="../styles/base.css" scoped></style>
