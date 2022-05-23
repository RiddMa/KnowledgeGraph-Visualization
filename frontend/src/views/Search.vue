<template>
  <v-container
    fluid
    id="graph-container"
    class="full-screen ma-0 pa-0 grow d-flex flex-column flex-nowrap"
  >
    <v-row class="fill-height">
      <v-col class="searchPanel mx-6 mt-10">
        <v-card class="pa-6" outlined raised>
          <v-row no-gutters>
            <v-col>
              <h2>搜索</h2>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-text-field
              v-model="keyword"
              append-icon="mdi-magnify"
              @keydown.enter="search()"
              @click:append="search()"
              placeholder="支持 cve_id, edb_id, cpe23uri"
              clearable
            >
            </v-text-field>
          </v-row>
        </v-card>
      </v-col>
      <knowledge-graph
        v-if="this.showGraph"
        class="searchResult grow"
        :graph-id="graphId"
      ></knowledge-graph>
    </v-row>
  </v-container>
</template>

<script>
// @ is an alias to /src
import { draw2DGraph } from "@/utils/graph";
import { mapState } from "vuex";
import KnowledgeGraph from "@/components/KnowledgeGraph";

export default {
  name: "Search",
  components: { KnowledgeGraph },
  data: () => ({
    keyword: "CVE-1999-0002",
    graphId: "search-graph",
    // showGraph: false,
    showGraph: true,
  }),
  computed: {
    ...mapState({
      graphStore: (state) => state.graphStore,
      graphData: (state) => state.graphData,
    }),
  },
  methods: {
    async draw2D() {
      draw2DGraph(this.graphData);
    },
    async search() {
      await this.$store.dispatch("fetchGraphSearch", {
        name: this.graphId,
        keyword: this.keyword,
      });
      this.showGraph = true;
    },
  },
  async mounted() {},
};
</script>

<style src="../styles/base.css"></style>
<style>
.searchPanel {
  position: absolute;
  z-index: 100;
  max-width: 480px;
}
.searchResult {
  position: absolute;
}
</style>
