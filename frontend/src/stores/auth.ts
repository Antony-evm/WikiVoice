import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { useChatStore } from "./chat";

export const useAuthStore = defineStore("auth", () => {
  const router = useRouter();

  // State - only non-sensitive data in localStorage
  // Auth tokens are now stored in HTTP-only cookies (not accessible to JS)
  const userId = ref<number | null>(
    localStorage.getItem("userId")
      ? parseInt(localStorage.getItem("userId")!)
      : null,
  );
  const email = ref<string | null>(localStorage.getItem("email"));
  const isLoggedIn = ref<boolean>(localStorage.getItem("isLoggedIn") === "true");

  // Computed - based on localStorage flag (cookies handle actual auth)
  const isAuthenticated = computed(() => isLoggedIn.value);

  // Actions
  function setUser(id: number, userEmail: string) {
    // If switching users, clear chat state to prevent data leakage
    if (userId.value !== null && userId.value !== id) {
      const chatStore = useChatStore();
      chatStore.clearAllState();
    }

    userId.value = id;
    email.value = userEmail;
    isLoggedIn.value = true;
    localStorage.setItem("userId", id.toString());
    localStorage.setItem("email", userEmail);
    localStorage.setItem("isLoggedIn", "true");
  }

  async function logout() {
    // Clear chat state FIRST to prevent data leakage to next user
    const chatStore = useChatStore();
    chatStore.clearAllState();

    // Call backend to clear HTTP-only cookies
    try {
      const api = (await import("@/api/client")).default;
      await api.post("/auth/logout");
    } catch {
      // Ignore errors during logout
    }

    // Clear local state
    userId.value = null;
    email.value = null;
    isLoggedIn.value = false;
    localStorage.removeItem("userId");
    localStorage.removeItem("email");
    localStorage.removeItem("isLoggedIn");

    router.push({ name: "auth" });
  }

  return {
    // State
    userId,
    email,
    // Computed
    isAuthenticated,
    // Actions
    setUser,
    logout,
  };
});
