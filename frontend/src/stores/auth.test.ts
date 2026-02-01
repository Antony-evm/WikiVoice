/**
 * Tests for auth store behavior.
 * Auth is now cookie-based - stytch_user_id cookie is checked for auth status.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";

// Mock vue-router
vi.mock("vue-router", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

// Helper to set a cookie in tests
function setCookie(name: string, value: string) {
  Object.defineProperty(document, "cookie", {
    writable: true,
    value: `${name}=${value}`,
  });
}

function clearCookie() {
  Object.defineProperty(document, "cookie", {
    writable: true,
    value: "",
  });
}

describe("Auth Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    clearCookie();
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

    it("should be authenticated when cookie and userId are present", async () => {
      localStorage.setItem("userId", "42");
      setCookie("stytch_user_id", "user-123");
      vi.resetModules();
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      expect(store.isAuthenticated).toBe(true);
    });

    it("should be authenticated when only cookie is present", async () => {
      setCookie("stytch_user_id", "user-123");
      vi.resetModules();
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      expect(store.isAuthenticated).toBe(true);
    });

    it("should be authenticated when only userId is present", async () => {
      localStorage.setItem("userId", "42");
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

    it("should be authenticated when cookie is also present", async () => {
      setCookie("stytch_user_id", "user-123");
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
  });

  describe("logout", () => {
    it("should clear userId", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      store.logout();

      expect(store.userId).toBeNull();
    });

    it("should clear email", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      store.logout();

      expect(store.email).toBeNull();
    });

    it("should set isAuthenticated to false", async () => {
      setCookie("stytch_user_id", "user-123");
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      store.logout();

      expect(store.isAuthenticated).toBe(false);
    });

    it("should remove userId from localStorage", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      store.logout();

      expect(localStorage.getItem("userId")).toBeNull();
    });

    it("should remove email from localStorage", async () => {
      const { useAuthStore } = await import("./auth");
      const store = useAuthStore();
      store.setUser(123, "user@example.com");

      store.logout();

      expect(localStorage.getItem("email")).toBeNull();
    });
  });
});
