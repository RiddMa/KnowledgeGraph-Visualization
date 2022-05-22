<template>
  <v-container
    fluid
    class="full-screen ma-0 pa-0 grow d-flex flex-column flex-nowrap"
  >
    <v-row class="grow ma-0 pa-0">
      <v-col class="grow ma-0 pa-0">
        <knowledge-graph></knowledge-graph>
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
  data: () => ({}),
  computed: {
    ...mapState({}),
  },
  mounted() {},
};
</script>

<style>
.full-screen {
  height: calc(100vh - 30px);
}
</style>
