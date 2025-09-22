<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <RouterView />
</template>

<style lang="scss">
html {
  overflow: -moz-scrollbars-none;
  -ms-overflow-style: none;
  height: 100%;
  body {
    height: 100%;
    margin: 0;
  }
  &::-webkit-scrollbar {
    width: 0 !important;
    display: none;
  }
}
html,
body,
#app {
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>
