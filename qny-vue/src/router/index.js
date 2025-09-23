import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "Login",
      component: () => import("../views/Login.vue"),
      meta: { requiresAuth: false },
    },
    {
      path: "/",
      redirect: "/agent-hall",
    },
    {
      path: "/agent-hall",
      name: "AgentHall",
      component: () => import("../views/AgentHall.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/my-agent",
      name: "MyAgent",
      component: () => import("../views/MyAgent.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/user-center",
      name: "UserCenter",
      component: () => import("../views/UserCenter.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/chat",
      name: "Chat",
      component: () => import("../views/Chat.vue"),
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("qny-token");
  if (to.meta.requiresAuth && !token) {
    next({ name: "Login" });
  } else {
    next();
  }
});

export default router;
