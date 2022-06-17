<template>
  <v-container
    fluid
    class="full-screen ma-0 pa-0 grow d-flex flex-column flex-nowrap"
  >
    <v-row class="grow ma-0 pa-0">
      <v-col class="grow ma-0 pa-0">
        <knowledge-graph :graph-id="graphId"></knowledge-graph>
      </v-col>
      <!--      <v-col v-if="visShowSideBar">-->
      <!--        -->
      <!--      </v-col>-->
    </v-row>
  </v-container>
</template>

<script>
import KnowledgeGraph from "@/components/KnowledgeGraph";
import { mapState } from "vuex";
export default {
  name: "Visualization",
  components: { KnowledgeGraph },
  data: () => ({
    graphId: "vis-graph",
  }),
  computed: {
    ...mapState({}),
  },
  mounted() {
    console.log("fetch");
    this.$store.dispatch("fetchGraphData", {
      name: this.graphId,
      limit: 30,
    });
  },
};
</script>

<style src="../styles/base.css"></style>
<style></style>
