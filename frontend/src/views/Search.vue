<template>
  <v-container fluid id="graph-container" class="ma-0" style="height: 96vh">
    <v-row>
      <v-col cols="4">
        <v-card class="pa-6">
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
    </v-row>
    <v-row>
      <v-col>
        <div id="2d-graph"></div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
// @ is an alias to /src
import { draw2DGraph } from "@/utils/graph";
import { mapState } from "vuex";

export default {
  name: "Search",
  components: {},
  data: () => ({
    keyword: "",
  }),
  computed: {
    ...mapState({
      graphData: (state) => state.graphData,
    }),
  },
  methods: {
    async draw2D() {
      draw2DGraph(this.graphData);
    },
    async search() {
      await this.$store.dispatch("fetchGraphSearch", this.keyword);
      draw2DGraph(this.graphData);
    },
  },
  async mounted() {},
};
</script>
