<template>
  <v-container fluid id="graph-container" class="ma-0" style="height: 95vh">
    <v-row>
      <v-col>
        <h1>{{ translation.graph_overview }}</h1>
        <v-btn onclick="this.sortStatItems('vul', this.graphStats['vul'])"></v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col v-for="(v, k) in overviewStats" :key="k" sm="12" md="6" lg="4">
        <v-card class="pa-6">
          <v-row>
            <v-col>
              <h2>{{ translation[k] }}</h2>
            </v-col>
          </v-row>
          <entry-list :entry-translate="translation" :vul-stats="v" />
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
      <v-col sm="12" md="6" lg="4">
        <v-card class="pa-6">
          <v-row>
            <v-col style="height: 300px">
              <stats-graph graph-id="vul"></stats-graph>
            </v-col>
          </v-row>
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
import _ from "lodash";
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
      vulStats: (state) => state.graphStats.vul,
      assetStats: (state) => state.graphStats.asset,
      exploitStats: (state) => state.graphStats.exploit,
    }),
  },
  methods: {
    sortStatItems(k, v) {
      console.log("k", k, "v", v);
      let kvArr = Object.entries(v).map(([key, value]) => ({ key, value }));
      console.log("kvarr is", kvArr);
      console.log(this.graphStatsOrder[k]);
      kvArr = kvArr.sort(function (a, b) {
        console.log(a, b);
        return (
          this.graphStatsOrder[k].indexOf(a.key) -
          this.graphStatsOrder[k].indexOf(b.key)
        );
      });
      // _.sortBy(kvArr, function (obj) {
      //   return _.indexOf(this.graphStatsOrder[k], obj.key);
      // });
      console.log("kvarr now", kvArr);
      return kvArr;
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
