<template>
  <v-container fluid id="graph-container" class="content-container-wide">
    <v-row class="px-6 pt-6 mb-0 pb-0">
      <v-col>
        <p class="text-h3 ma-0">控制台</p>
      </v-col>
    </v-row>

    <v-row class="mt-0 pt-0">
      <v-col cols="12" sm="12" md="6">
        <v-card class="pa-6" outlined raised>
          <v-row class="align-baseline">
            <v-col>
              <span class="text-h4">运行状态</span>
            </v-col>
            <v-col class="text-h5">
              {{ runningTask }}/{{ totalTask }} 运行中
            </v-col>
          </v-row>
          <v-row
            v-for="(v, k) in services"
            v-bind:key="k"
            class="text-body-1 align-baseline"
          >
            <v-col> {{ v.name }} </v-col>
            <v-col>
              <v-btn
                v-if="v.running"
                raised
                color="red darken-2"
                class="white--text text-button"
                @click="terminateJob(v)"
              >
                停止
              </v-btn>
              <v-btn
                v-else
                raised
                color="green darken-2"
                class="white--text text-button"
                @click="dispatchJob(v)"
              >
                启动
              </v-btn>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapState } from "vuex";

export default {
  name: "Dashboard",
  data: () => ({}),
  computed: {
    ...mapState({
      services: (state) => state.dashboardStore.services,
    }),
    totalTask() {
      return this.services.length;
    },
    runningTask() {
      return this.services.filter((obj) => {
        return !!obj.running;
      }).length;
    },
  },
  methods: {
    async dispatchJob(v) {
      await this.$store.dispatch("dispatchJob", v.id);
      v.running = true;
    },
    async terminateJob(v) {
      await this.$store.dispatch("terminateJob", v.id);
      v.running = false;
    },
  },
  mounted() {},
};
</script>
<style src="../styles/base.css" scoped></style>
