<template>
  <v-container fluid class="fill-height">
    <div :id="graphId" class="vis-graph"></div>
    <!--    <v-card-->
    <!--      v-if="visSidePanelActive"-->
    <!--      v-click-outside="onCloseSidePanel"-->
    <!--      id="overlay"-->
    <!--      class="sidePanel pa-0"-->
    <!--      outlined-->
    <!--      raised-->
    <!--    >-->
    <v-card
      v-if="visSidePanelActive"
      id="overlay"
      class="sidePanel pa-0"
      outlined
      raised
    >
      <div v-if="dataType === 'Vulnerability'" class="sidePanelDiv">
        <v-btn class="closePanelButton" fab small @click="onCloseSidePanel">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-row class="my-0 ml-4 mr-2 pa-0">
          <v-col class="py-6">
            <p class="text-h5 sidePanelTitle">漏洞</p>
            <p class="text-body-1 sidePanelContent">
              {{ this.sideBarData["vuln"]["cve_id"] }}
              <v-divider class="mt-2"></v-divider>
            </p>
            <p></p>
            <p class="text-h6 sidePanelContent">基础信息</p>
            <p class="text-body-1 sidePanelContent">
              数据格式版本：{{ this.sideBarData["version"] }}
            </p>
            <p class="text-body-1 sidePanelContent">
              数据更新日期：{{ mmt(this.sideBarData["timestamp"]).format() }}
            </p>
            <p class="text-body-1 sidePanelContent">
              数据更新日期：{{
                mmt(this.sideBarData["vuln"]["last_update_date"]).format()
              }}
            </p>
            <p class="text-body-1 sidePanelContent">
              数据更新日期：{{
                mmt(this.sideBarData["vuln"]["publish_date"]).format()
              }}
            </p>
            <p class="text-body-1 sidePanelContent">
              描述：{{ this.sideBarData["vuln"]["desc"] }}
            </p>
            <p class="text-body-1 sidePanelContent">
              CWE 类型：{{ this.sideBarData["vuln"]["cwe_id"] }}
            </p>
            <p class="text-h6 sidePanelContent">风险评估</p>
            <v-row v-if="this.sideBarData['vuln']['impact']['baseMetricV3']">
              <v-col> </v-col>
            </v-row>
            <v-row
              v-else-if="this.sideBarData['vuln']['impact']['baseMetricV2']"
              class="ma-0 pa-0"
            >
              <v-col class="mt-2 pa-0">
                <v-row no-gutters class="ma-0 pa-0">
                  <v-col>
                    <span class="text-body-1 sidePanelContent">
                      综合指数：{{ this.cvss["cvssV2"]["baseScore"] }} /
                      {{ this.cvss["severity"] }}
                    </span>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col>
                    <span class="text-body-1 sidePanelContent">
                      利用指数：{{ this.cvss["exploitabilityScore"] }}
                    </span>
                  </v-col>
                  <v-col>
                    <span class="text-body-1 sidePanelContent">
                      影响指数：{{ this.cvss["impactScore"] }}
                    </span>
                  </v-col>
                </v-row>
                <p class="text-body-1 sidePanelContent">
                  CVSS 向量：{{ this.cvss["cvssV2"]["vectorString"] }}
                </p>
              </v-col>
            </v-row>
            <p v-else class="text-body-1 sidePanelContent">暂无内容</p>
            <p class="text-h6 sidePanelContent">参考资料</p>
            <v-row
              v-for="ref in this.sideBarData['vuln']['references']"
              v-bind:key="ref['name']"
              class="ma-0 pa-0"
            >
              <v-col class="mt-2 pa-0">
                <p class="text-body-1 ma-0 pa-0">
                  链接：<a :href="ref['url']">{{ ref["url"] }}</a>
                </p>
                <p class="text-body-1 ma-0 pa-0">
                  来源：{{ ref["refsource"] }}
                </p>
                <v-row no-gutters>
                  <v-col v-if="ref['tags'].length > 0" class="grow text-body-1">
                    标签：<span v-for="tag in ref['tags']" v-bind:key="tag"
                      >{{ tag }},&nbsp;
                    </span>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </div>

      <div v-if="dataType === 'Family'" class="sidePanelDiv">
        <v-btn class="closePanelButton" fab small @click="onCloseSidePanel">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-row class="my-0 ml-4 mr-2 pa-0">
          <v-col class="py-6">
            <p class="text-h5 sidePanelTitle">资产家族</p>
            <p class="text-body-1 sidePanelContent">
              {{ this.sideBarData["cpe23uri"] }}
              <v-divider class="mt-2"></v-divider>
            </p>
            <p class="text-h6 sidePanelContent">基础信息</p>
            <p class="text-body-1 sidePanelContent">数据格式版本：CPE 2.3</p>
            <p class="text-body-1 sidePanelContent">
              制造商：{{ this.sideBarData["vendor"] }}
            </p>
            <p class="text-body-1 sidePanelContent">
              产品：{{ this.sideBarData["product"] }}
            </p>
            <v-row no-gutters>
              <v-col
                v-if="this.sideBarData['type'].length > 0"
                class="mt-2 pa-0 text-body-1"
              >
                标签：<span
                  v-for="tag in this.sideBarData['type']"
                  v-bind:key="tag"
                  >{{ tag }},&nbsp;
                </span>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </div>

      <div v-if="dataType === 'Asset'" class="sidePanelDiv">
        <v-btn class="closePanelButton" fab small @click="onCloseSidePanel">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-row class="my-0 ml-4 mr-2 pa-0">
          <v-col class="py-6">
            <p class="text-h5 sidePanelTitle">资产</p>
            <p class="text-body-1 sidePanelContent">
              {{ this.sideBarData["cpe23uri"] }}
              <v-divider class="mt-2"></v-divider>
            </p>
            <p class="text-h6 sidePanelContent">基础信息</p>
            <p class="text-body-1 sidePanelContent">
              数据格式版本：CPE 2.3
            </p>
            <p class="text-body-1 sidePanelContent">
              数据更新日期：{{ mmt(this.sideBarData["timestamp"]).format() }}
            </p>
            <p class="text-body-1 sidePanelContent">
              资产名称：{{this.sideBarData['title']}}
            </p>
            <p class="text-body-1 sidePanelContent">
              类型：{{this.sideBarData['field']['part']}}
            </p>
            <p class="text-body-1 sidePanelContent">
              制造商：{{this.sideBarData['field']['vendor']}}
            </p>
            <p class="text-body-1 sidePanelContent">
              产品：{{this.sideBarData['field']['product']}}
            </p>
            <p class="text-body-1 sidePanelContent">
              版本：{{this.sideBarData['field']['version']}}
            </p>
          </v-col>
        </v-row>
      </div>
    </v-card>
  </v-container>
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
import { fullVizFormatter } from "@/utils/eChartsTooltipConfig";
import _ from "lodash";
import moment from "moment";
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
    sideBarData: undefined,
    dataType: "",
    mmt: moment,
  }),
  computed: {
    ...mapState({
      graph: (state) => state.graph,
      graphData: (state) => state.graphData,
      visSidePanelActive: (state) => state.view.visSidePanelActive,
    }),
    cvssType() {
      if (!this.sideBarData) {
        return undefined;
      }
      if (this.sideBarData["vuln"]["impact"]["baseMetricV3"]) {
        return 3;
      } else {
        return 2;
      }
    },
    cvss() {
      if (this.sideBarData) {
        return this.sideBarData["vuln"]["impact"]["baseMetricV2"];
      } else {
        return undefined;
      }
    },
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
          limit: 50,
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
              // focus: "adjacency",
              lineStyle: {
                width: 10,
              },
            },
            select: {
              disabled: false,
            },
            selectMode: "single",
            // autoCurveness: true,
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
      this.graph[this.graphId].on("selectchanged", (params) =>
        this.forceDirectedGraphSelectHandler(params)
      );
    },
    forceDirectedGraphSelectHandler(params) {
      // console.log(params);
      switch (params.fromActionPayload.dataType) {
        case "node":
          this.onNodeSelected(params);
          break;
        case "edge":
          this.onEdgeSelected(params);
          break;
      }
    },
    onNodeSelected(params) {
      this.$store.commit("setVisShowSideBar", true);
      this.sideBarData =
        this.graphData[this.graphId].nodes[
          params.fromActionPayload.dataIndexInside
        ];
      if (this.sideBarData.type.includes("Vulnerability")) {
        this.dataType = "Vulnerability";
        this.sideBarData = JSON.parse(this.sideBarData.props);
      } else if (this.sideBarData.type.includes("Family")) {
        this.dataType = "Family";
        let splitUri = this.sideBarData["cpe23uri"].split(":");
        this.sideBarData["vendor"] = splitUri[3];
        this.sideBarData["product"] = splitUri[4];
      } else if (this.sideBarData.type.includes("Asset")) {
        this.dataType = "Asset";
        this.sideBarData = JSON.parse(this.sideBarData.props);
      } else if (this.sideBarData.type.includes("Exploit")) {
        this.dataType = "Exploit";
      }
      console.log(this.sideBarData);
    },
    onEdgeSelected(params) {
      this.sideBarData =
        this.graphData[this.graphId].links[
          params.fromActionPayload.dataIndexInside
        ];
    },
    onResize() {
      // console.log(window.innerWidth, window.innerHeight);
      this.graph[this.graphId].resize();
    },
    onCloseSidePanel() {
      this.$store.commit("setVisShowSideBar", false);
    },
  },

  mounted() {
    this.drawVisGraph();
    window.addEventListener("resize", _.debounce(this.onResize, 300));
    this.mmt.locale("zh-cn");
    this.mmt.defaultFormat = "L";
  },
  beforeDestroy() {
    this.graph[this.graphId].dispose();
    window.removeEventListener("resize", _.debounce(this.onResize, 300));
  },
};
</script>

<style scoped>
.sidePanel {
  position: fixed;
  top: 24px;
  right: 0;
  z-index: 100;
}
knowledge-graph,
#overlay {
  position: absolute;
}
#overlay {
  max-width: 500px;
  max-height: 90vh !important;
}
.sidePanelTitle {
  margin: 0;
}
.sidePanelContent {
  margin: 6px 0 0 0;
}
.a-inline {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  /* number of lines to show */
  line-clamp: 1;
  -webkit-box-orient: vertical;
}
.sidePanelDiv {
  max-height: 89vh;
  overflow-y: auto;
}
.closePanelButton {
  position: absolute;
  top: 16px;
  right: 24px;
}
</style>
