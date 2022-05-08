<template>
  <v-list class="ma-0">
    <!--    <v-list-item-group>-->
    <v-list-item
      v-for="(v, k) in vulStats"
      :key="k"
      class="pa-0 ma-0"
    >
      <v-list-item-content>
        <!--        <v-list-item-title>{{ entryTranslate[k] }}</v-list-item-title>-->
        {{ entryTranslate[k] }}
      </v-list-item-content>
      <v-list-item-content>{{ v }}</v-list-item-content>
    </v-list-item>
    <!--    </v-list-item-group>-->
  </v-list>
</template>
<script>
export default {
  name: "entry-list",
  props: {
    entryTranslate: {},
    vulStats: {}
  }
};
</script>
