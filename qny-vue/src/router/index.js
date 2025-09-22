import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: () => import("../views/main/main.vue"),
    },
    {
      path: "/login",
      component: () => import("../views/main/login.vue"),
    },
  ],
});

export default router;
