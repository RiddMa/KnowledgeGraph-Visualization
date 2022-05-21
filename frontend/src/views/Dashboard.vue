<template>
  <v-container fluid id="graph-container" class="content-container-wide">
    <v-row class="px-6 pt-6 mb-0 pb-0">
      <v-col>
        <p class="text-h3 ma-0">控制台</p>
      </v-col>
    </v-row>

    <v-row class="mt-0 pt-0">
      <v-col cols="12" sm="12" md="6" lg="4">
        <v-card class="pa-6" outlined raised>
        </v-card>
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
  data: () => ({
    assetChartToggle: 0,
    showAssetFamily: true,
  }),
  computed: {
    ...mapState({
      translation: (state) => state.translation,
      graphStats: (state) => state.graphStats,
      graphStatsOrder: (state) => state.graphStatsOrder,
      graphData: (state) => state.graphData,
      overviewStats: (state) => state.graphStats,
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
