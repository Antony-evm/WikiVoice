import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/HomeView.vue"),
    },
    {
      path: "/architecture",
      name: "architecture",
      component: () => import("@/views/ArchitectureView.vue"),
    },
    {
      path: "/roadmap",
      name: "roadmap",
      component: () => import("@/views/RoadmapView.vue"),
    },
    {
      path: "/auth",
      name: "auth",
      component: () => import("@/views/AuthView.vue"),
      meta: { guest: true },
    },
    {
      path: "/login",
      redirect: "/auth",
    },
    {
      path: "/register",
      redirect: "/auth",
    },
    {
      path: "/chat",
      name: "chat",
      component: () => import("@/views/ChatView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/chat/:sessionId",
      name: "chat-session",
      component: () => import("@/views/ChatView.vue"),
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: "auth" });
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: "chat" });
  } else {
    next();
  }
});

export default router;
