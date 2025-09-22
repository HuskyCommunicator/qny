<script setup>
import { RouterLink, RouterView } from "vue-router";
import Nav from "@/components/nav.vue";
import Aside from "@/components/aside.vue";
</script>

<template>
  <div class="app-container">
    <Nav />
    <div class="main-content">
      <Aside />
      <RouterView />
    </div>
  </div>
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

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  width: 100%;
}

Aside {
  width: 200px;
  height: 100%;
  background: #f5f5f5;
}
</style>
