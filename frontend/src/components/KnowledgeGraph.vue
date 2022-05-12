<template>
  <div :id="graphId" class="vis-graph"></div>
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
import localeCfg from "@/utils/langZH.ts";
import { mapState } from "vuex";
import { fullVizFormatter } from "@/utils/tooltipConfig";
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GraphChart,
  CanvasRenderer,
]);
echarts.registerLocale("ZH", localeCfg);

export default {
  name: "KnowledgeGraph",
  props: {},
  data: () => ({
    // graph: undefined,
    graphId: "vis-graph",
    categories: [
      { name: "漏洞", tooltip: "CVE 漏洞条目" },
      { name: "家族", tooltip: "来自同一制造商同一软件名的 CPE 资产家族" },
      { name: "资产", tooltip: "CPE 资产" },
      { name: "应用程序", tooltip: "CPE 应用程序资产" },
      { name: "操作系统", tooltip: "CPE 操作系统资产" },
      { name: "硬件", tooltip: "CPE 硬件资产" },
      { name: "利用", tooltip: "针对 CVE 漏洞的利用代码" },
    ],
    // categories: [
    //   { name: "漏洞", symbolSize: 50, tooltip: "CVE 漏洞条目" },
    //   {
    //     name: "家族",
    //     symbolSize: 50,
    //     tooltip: "来自同一制造商同一软件名的 CPE 资产家族",
    //   },
    //   { name: "资产", symbolSize: 15, tooltip: "CPE 资产" },
    //   { name: "应用程序", symbolSize: 15, tooltip: "CPE 应用程序资产" },
    //   { name: "操作系统", symbolSize: 15, tooltip: "CPE 操作系统资产" },
    //   { name: "硬件", symbolSize: 15, tooltip: "CPE 硬件资产" },
    //   { name: "利用", symbolSize: 50, tooltip: "针对 CVE 漏洞的利用代码" },
    // ],
  }),
  computed: {
    ...mapState({
      graph: (state) => state.graph,
      graphData: (state) => state.graphData,
    }),
  },
  methods: {
    async drawVisGraph() {
      this.$store.commit("setGraph", {
        name: this.graphId,
        graph: echarts.init(document.getElementById(this.graphId), null, {
          useDirtyRect: true,
          locale: "ZH",
        }),
      });
      this.graph[this.graphId].showLoading();
      if (!this.graphData[this.graphId]) {
        await this.$store.dispatch("fetchGraphData", {
          name: this.graphId,
          limit: 100,
        });
      }
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
          data: this.graphData[this.graphId].categories,
          top: 24,
          left: "center",
          tooltip: {
            show: true,
            confine: true,
            trigger: "item",
            // renderMode: "richText",
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
            data: this.graphData[this.graphId].nodes,
            links: this.graphData[this.graphId].links,
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
              textStyle: {
                width: 400,
                overflow: "break",
              },
              formatter: (params) => fullVizFormatter(params),
            },
          },
        ],
      };
      this.graph[this.graphId].hideLoading();
      this.graph[this.graphId].setOption(option);
    },
  },
  mounted() {
    this.drawVisGraph();
  },
  beforeDestroy() {
    this.graph[this.graphId].dispose();
  },
};
</script>

<style scoped></style>
