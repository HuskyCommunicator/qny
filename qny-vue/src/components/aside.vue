<script setup>
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
} from "@element-plus/icons-vue";
import { useRoute } from "vue-router";
import { computed } from "vue";

const route = useRoute();

const routeToIndexMap = {
  "/": "/",
  "/my-agent": "/my-agent",
  "/user-center": "/user-center",
};

const activeIndex = computed(() => routeToIndexMap[route.path] || "/");

const handleOpen = (key, keyPath) => {
  console.log(key, keyPath);
};
const handleClose = (key, keyPath) => {
  console.log(key, keyPath);
};
</script>

<template>
  <!-- 侧边栏已隐藏，不渲染任何内容 -->
</template>

<style lang="scss" scoped></style>
