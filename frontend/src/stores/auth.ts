import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

/**
 * Get a cookie value by name.
 * The stytch_user_id cookie is readable (not httpOnly) to check auth status.
 */
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match?.[2] ? decodeURIComponent(match[2]) : null;
}

export const useAuthStore = defineStore("auth", () => {
  const router = useRouter();

  // State - only non-sensitive user info stored in localStorage
  const userId = ref<number | null>(
    localStorage.getItem("userId")
      ? parseInt(localStorage.getItem("userId")!)
      : null,
  );
  const email = ref<string | null>(localStorage.getItem("email"));

  // Computed - check stytch_user_id cookie for auth status
  const isAuthenticated = computed(() => {
    // Check for stytch_user_id cookie (set by backend, readable by frontend)
    const stytchUserId = getCookie("stytch_user_id");
    return !!stytchUserId && !!userId.value;
  });

  // Actions
  function setUser(id: number, userEmail: string) {
    userId.value = id;
    email.value = userEmail;
    localStorage.setItem("userId", id.toString());
    localStorage.setItem("email", userEmail);
  }

  function logout() {
    userId.value = null;
    email.value = null;
    localStorage.removeItem("userId");
    localStorage.removeItem("email");
    // Clear auth cookies by setting them to expire
    document.cookie = "stytch_user_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
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
