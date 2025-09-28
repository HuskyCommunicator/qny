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
  <el-menu
    :default-active="activeIndex"
    class="el-menu-vertical-demo"
    @open="handleOpen"
    @close="handleClose"
    router
  >
    <el-menu-item index="/">
      <el-icon><icon-menu /></el-icon>
      <span>智能体大厅</span>
    </el-menu-item>
    <!-- <el-menu-item index="/my-agent">
      <el-icon><icon-menu /></el-icon>
      <span>我的智能体</span>
    </el-menu-item> -->
    <el-menu-item index="/user-center">
      <el-icon><User /></el-icon>
      <span>个人中心</span>
    </el-menu-item>
    <!-- <el-menu-item index="/chat">
      <el-icon><ChatSquare /></el-icon>
      <span>聊天</span>
    </el-menu-item>
    <el-menu-item index="/chat-history">
      <el-icon><Document /></el-icon>
      <span>聊天历史</span>
    </el-menu-item> -->
  </el-menu>
</template>

<style lang="scss" scoped></style>
