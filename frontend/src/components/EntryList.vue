<template>
  <v-list class="mx-0 mt-2 mb-0 pa-0">
    <v-row v-for="item in vulStats" :key="item[0]" class="px-0 py-2 ma-0">
<!--      <v-col sm="12" md="8" class="ma-0 pa-0">-->
      <v-col cols="8" md="7" class="ma-0 pa-0">
        {{ entryTranslate[item[0]] }}
      </v-col>
<!--      <v-col sm="12" md="4" class="ma-0 pa-0">-->
      <v-col cols="4" md="5" class="ma-0 pa-0">
        {{ formatNumber(item[1]) }}
      </v-col>
    </v-row>

    <!--    &lt;!&ndash;    <v-list-item-group>&ndash;&gt;-->
    <!--    <v-list-item v-for="(v, k) in vulStats" :key="k" class="pa-0 ma-0">-->
    <!--      <v-list-item-content class="list-k">-->
    <!--        &lt;!&ndash;        <v-list-item-title>{{ entryTranslate[k] }}</v-list-item-title>&ndash;&gt;-->
    <!--        {{ entryTranslate[k] }}-->
    <!--      </v-list-item-content>-->
    <!--      <v-list-item-content class="list-v">{{ v }}</v-list-item-content>-->
    <!--    </v-list-item>-->
    <!--    &lt;!&ndash;    </v-list-item-group>&ndash;&gt;-->
  </v-list>
</template>
<script>
export default {
  name: "entry-list",
  props: {
    entryTranslate: {},
    vulStats: {},
  },
  methods: {
    formatNumber(n) {
      return n.toLocaleString("en", { useGrouping: true });
    },
  },
};
</script>
<style>
.list-k {
  flex-grow: 1;
  flex-shrink: 1;
  flex-basis: auto;
}
.list-v {
  flex-shrink: 1;
  flex-basis: 0;
}
</style>
