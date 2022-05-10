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
    // graphData: undefined,
    graph: undefined,
    categories: [
      { name: "漏洞", symbolSize: 50, tooltip: "CVE 漏洞条目" },
      {
        name: "家族",
        symbolSize: 50,
        tooltip: "来自同一制造商同一软件名的 CPE 资产家族",
      },
      { name: "资产", symbolSize: 15, tooltip: "CPE 资产" },
      { name: "应用程序", symbolSize: 15, tooltip: "CPE 应用程序资产" },
      { name: "操作系统", symbolSize: 15, tooltip: "CPE 操作系统资产" },
      { name: "硬件", symbolSize: 15, tooltip: "CPE 硬件资产" },
      { name: "利用", symbolSize: 50, tooltip: "针对 CVE 漏洞的利用代码" },
    ],
    tmp: undefined,
  }),
  computed: {
    ...mapState({
      graphData: (state) => state.graphData,
    }),
  },
  methods: {
    async drawVisGraph() {
      this.graph = echarts.init(document.getElementById("vis-graph"), null, {});
      this.graph.showLoading();
      // this.graphData = await this.$store.dispatch("fetchGraphData", 40);
      await this.$store.dispatch("fetchGraphData", 40);
      let option = {
        title: {
          text: "漏洞知识图谱 VulKG",
          subtext: "Default layout",
          top: "bottom",
          left: "right",
        },
        tooltip: {
          show: true,
          confine: true,
        },
        legend: {
          data: this.graphData.categories,
          top: 24,
          tooltip: {
            show: true,
            confine: true,
            trigger: "item",
            // formatter: function (params) {
            //   console.log(params);
            //   return this.categories[params.legendIndex]["tooltip"];
            // },
          },
        },
        animation: true,
        animationThreshold: 10000,
        animationDuration: 1500,
        animationEasingUpdate: "quinticInOut",
        stateAnimation: {
          duration: 300,
          easing: "cubicOut",
        },
        series: [
          {
            id: "vis-full-graph",
            name: "VulKG",
            type: "graph",
            layout: "force",
            // layout: "circular",
            data: this.graphData.nodes,
            links: this.graphData.links,
            categories: this.categories,
            roam: true,
            label: {
              show: false,
              position: "right",
            },
            draggable: true,
            force: {
              initLayout: "circular",
              repulsion: 400,
              gravity: 0.1,
              friction: 0.1,
              edgeLength: [100, 200],
            },
            edgeSymbol: ["none", "arrow"],
            edgeSymbolSize: 5,
            // edgeLabel: {
            //   show: true,
            //   formatter: function (params) {
            //     return params.data.category;
            //   },
            // },
            lineStyle: {
              width: 2,
              color: "source",
            },
            emphasis: {
              focus: "adjacency",
              lineStyle: {
                width: 10,
              },
            },
            select: {
              disabled: false,
            },
            selectMode: "single",
            autoCurveness: true,
            tooltip: {

            },
          },
        ],
      };
      this.graph.hideLoading();
      this.graph.setOption(option);
      this.tmp = option;
    },
  },
  mounted() {
    // this.graphData=
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
