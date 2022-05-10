<template>
  <div id="vis-graph" class="vis-graph"></div>
</template>

<script>
import * as echarts from "echarts/core";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from "echarts/components";
import { GraphChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";
import { mapState } from "vuex";
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GraphChart,
  CanvasRenderer,
]);

export default {
  name: "Graph",
  props: {},
  data: () => ({
    filepath:
      "https://cdn.jsdelivr.net/gh/apache/echarts-website@asf-site/examples/data/asset/data/les-miserables.json",
    graph: undefined,
    graphData: undefined,
    categories: [
      { name: "漏洞", symbolSize: 40 },
      { name: "家族", symbolSize: 25 },
      { name: "资产", symbolSize: 15 },
      { name: "应用程序", symbolSize: 15 },
      { name: "操作系统", symbolSize: 15 },
      { name: "硬件", symbolSize: 15 },
      { name: "利用", symbolSize: 25 },
    ],
    formatter: function (params) {},
  }),
  computed: {
    ...mapState({}),
  },
  methods: {
    async drawVisGraph() {
      this.graph = echarts.init(document.getElementById("vis-graph"), null, {});
      this.graph.showLoading();
      let option;
      this.graphData = await this.$store.dispatch("fetchGraphData", 30);
      option = {
        title: {
          text: "漏洞知识图谱 VulKG",
          subtext: "Default layout",
          top: "bottom",
          left: "right",
        },
        tooltip: {},
        legend: [
          {
            // selectedMode: 'single',
            data: this.graphData.categories.map(function (a) {
              return a.name;
            }),
          },
        ],
        series: [
          {
            id: "vis-full-graph",
            name: "VulKG",
            type: "graph",
            layout: "force",
            data: this.graphData.nodes,
            links: this.graphData.links,
            categories: this.categories,
            roam: true,
            label: {
              show: false,
              position: "right",
            },
            force: {
              repulsion: 200,
              gravity: 0.7,
              friction: 0.1,
              // edgeLength:[20,80]
            },
          },
        ],
      };
      this.graph.hideLoading();
      this.graph.setOption(option);
    },
  },
  mounted() {
    this.drawVisGraph();
  },
};
</script>

<style scoped>
.vis-graph {
  width: 100%;
  height: 100%;
}
</style>
