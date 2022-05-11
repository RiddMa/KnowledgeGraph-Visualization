<template>
  <div :id="graphId" class="vis-graph"></div>
</template>

<script>
import * as echarts from "echarts/core";
import { TooltipComponent, LegendComponent } from "echarts/components";
import { PieChart } from "echarts/charts";
import { LabelLayout } from "echarts/features";
import { CanvasRenderer } from "echarts/renderers";
import { mapState } from "vuex";
import localeCfg from "@/utils/langZH.ts";
echarts.use([
  TooltipComponent,
  LegendComponent,
  PieChart,
  CanvasRenderer,
  LabelLayout,
]);
echarts.registerLocale("ZH", localeCfg);
export default {
  name: "StatsGraph",
  props: {
    graphId: String,
    data: {},
  },
  data: () => ({}),
  computed: {
    ...mapState({
      graph: (state) => state.graph,
      graphData: (state) => state.graphData,
    }),
  },
  methods: {
    async drawStatsGraph() {
      this.$store.commit("setGraph", {
        name: this.graphId,
        graph: echarts.init(document.getElementById(this.graphId), null, {
          locale: "ZH",
        }),
      });
      this.graph[this.graphId].showLoading();
      let option = {
        tooltip: {
          trigger: "item",
        },
        legend: {
          top: 0,
          left: "center",
        },
        series: [
          {
            name: "受影响资产分布",
            type: "pie",
            radius: ["30%", "70%"],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: "#fff",
              borderWidth: 2,
            },
            label: {
              show: true,
              position: "inside",
            },
            emphasis: {
              label: {
                show: true,
                fontSize: "24",
                fontWeight: "bold",
              },
            },
            // labelLine: {
            //   show: false,
            // },
            data: [
              { value: 1048, name: "Search Engine" },
              { value: 735, name: "Direct" },
              { value: 580, name: "Email" },
              { value: 484, name: "Union Ads" },
              { value: 300, name: "Video Ads" },
            ],
          },
        ],
      };
      this.graph[this.graphId].hideLoading();
      this.graph[this.graphId].setOption(option);
    },
  },
  mounted() {
    this.drawStatsGraph();
  },
};
</script>

<style scoped></style>
