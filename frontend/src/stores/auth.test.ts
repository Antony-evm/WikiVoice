/**
 * Tests for auth store behavior.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";

// Mock vue-router
vi.mock("vue-router", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

// Mock api client
vi.mock("@/api/client", () => ({
  default: {
    post: vi.fn(),
  },
}));

describe("Auth Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe("Initial State", () => {
    it("should have null userId when localStorage is empty", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      expect(store.userId).toBeNull();
    });

    it("should have null email when localStorage is empty", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      expect(store.email).toBeNull();
    });

    it("should not be authenticated when localStorage is empty", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      expect(store.isAuthenticated).toBe(false);
    });

    it("should restore userId from localStorage", async () => {
      localStorage.setItem("userId", "42");
      vi.resetModules();
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      expect(store.userId).toBe(42);
    });

    it("should restore email from localStorage", async () => {
      localStorage.setItem("email", "test@example.com");
      vi.resetModules();
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      expect(store.email).toBe("test@example.com");
    });

    it("should restore isAuthenticated from localStorage", async () => {
      localStorage.setItem("isLoggedIn", "true");
      vi.resetModules();
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      expect(store.isAuthenticated).toBe(true);
    });
  });

  describe("setUser", () => {
    it("should set userId correctly", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();

      store.setUser(123, "user@example.com");

      expect(store.userId).toBe(123);
    });

    it("should set email correctly", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();

      store.setUser(123, "user@example.com");

      expect(store.email).toBe("user@example.com");
    });

    it("should set isAuthenticated to true", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();

      store.setUser(123, "user@example.com");

      expect(store.isAuthenticated).toBe(true);
    });

    it("should persist userId to localStorage", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();

      store.setUser(123, "user@example.com");

      expect(localStorage.getItem("userId")).toBe("123");
    });

    it("should persist email to localStorage", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();

      store.setUser(123, "user@example.com");

      expect(localStorage.getItem("email")).toBe("user@example.com");
    });

    it("should persist isLoggedIn to localStorage", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();

      store.setUser(123, "user@example.com");

      expect(localStorage.getItem("isLoggedIn")).toBe("true");
    });
  });

  describe("logout", () => {
    it("should clear userId", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      await store.logout();

      expect(store.userId).toBeNull();
    });

    it("should clear email", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      await store.logout();

      expect(store.email).toBeNull();
    });

    it("should set isAuthenticated to false", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      await store.logout();

      expect(store.isAuthenticated).toBe(false);
    });

    it("should remove userId from localStorage", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      await store.logout();

      expect(localStorage.getItem("userId")).toBeNull();
    });

    it("should remove email from localStorage", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      await store.logout();

      expect(localStorage.getItem("email")).toBeNull();
    });

    it("should remove isLoggedIn from localStorage", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      await store.logout();

      expect(localStorage.getItem("isLoggedIn")).toBeNull();
    });

    it("should call backend logout endpoint", async () => {
      const api = (await import("@/api/client")).default;
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      await store.logout();

      expect(api.post).toHaveBeenCalledWith("/auth/logout");
    });

    it("should handle backend logout errors gracefully", async () => {
      const api = (await import("@/api/client")).default;
      vi.mocked(api.post).mockRejectedValueOnce(new Error("Network error"));

      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      // Should not throw
      await expect(store.logout()).resolves.toBeUndefined();
      expect(store.isAuthenticated).toBe(false);
    });
  });
});
