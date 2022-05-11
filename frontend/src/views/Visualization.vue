<template>
  <v-container fluid class="full-screen ma-0 pa-0 grow d-flex flex-column flex-nowrap">
    <v-row class="grow ma-0 pa-0">
      <v-col class="grow ma-0 pa-0">
        <graph></graph>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Graph from "@/components/KnowledgeGraph";
export default {
  name: "Visualization",
  components: { Graph },
};
</script>

<style>
.full-screen {
  height: calc(100vh - 30px);
}
</style>
