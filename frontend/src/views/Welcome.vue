<template>
  <v-container fluid class="full-screen">
    <v-row>
      <v-col class="d-flex justify-center">
        <v-card class="welcome-card pa-6 grow" outlined raised>
          <v-row>
            <v-col class="text-center">
              <span class="text-h3">欢迎</span>
            </v-col>
          </v-row>
          <v-row>
            <v-col class="text-center">
              <span class="text-h5">点击左侧列表中的任意视图以开始。</span>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "Welcome",
};
</script>

<style scoped>
.welcome-card {
  margin-top: 5vh;
  max-width: 640px;
}
</style>
