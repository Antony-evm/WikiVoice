/**
 * Tests for chat store behavior.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import type { Session, Query } from "./chat";

// Mock api client - use function factory for hoisting
vi.mock("@/api/client", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

// Import mock after vi.mock
import api from "@/api/client";
import { useChatStore } from "./chat";

// Cast api methods for mocking
const mockedApi = vi.mocked(api, { deep: true });

describe("Chat Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  describe("Initial State", () => {
    it("should have empty sessions array", () => {
      const store = useChatStore();
      expect(store.sessions).toEqual([]);
    });

    it("should have null currentSession", () => {
      const store = useChatStore();
      expect(store.currentSession).toBeNull();
    });

    it("should have empty queries array", () => {
      const store = useChatStore();
      expect(store.queries).toEqual([]);
    });

    it("should not be loading initially", () => {
      const store = useChatStore();
      expect(store.isLoading).toBe(false);
    });

    it("should not be sending initially", () => {
      const store = useChatStore();
      expect(store.isSending).toBe(false);
    });
  });

  describe("fetchSessions", () => {
    it("should set isLoading to true while fetching", async () => {
      const store = useChatStore();
      mockedApi.get.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () => resolve({ data: { data: { sessions: [] } } } as any),
              100,
            ),
          ),
      );

      const promise = store.fetchSessions();
      expect(store.isLoading).toBe(true);
      await promise;
    });

    it("should set isLoading to false after fetching", async () => {
      const store = useChatStore();
      mockedApi.get.mockResolvedValueOnce({
        data: { data: { sessions: [] } },
      } as any);

      await store.fetchSessions();

      expect(store.isLoading).toBe(false);
    });

    it("should populate sessions with response data", async () => {
      const store = useChatStore();
      const mockSessions: Session[] = [
        {
          session_id: 1,
          title: "Test Session",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        },
        {
          session_id: 2,
          title: "Another Session",
          created_at: "2024-01-02",
          updated_at: "2024-01-02",
        },
      ];
      mockedApi.get.mockResolvedValueOnce({
        data: { data: { sessions: mockSessions } },
      } as any);

      await store.fetchSessions();

      expect(store.sessions).toEqual(mockSessions);
    });

    it("should handle fetch errors gracefully", async () => {
      const store = useChatStore();
      const consoleSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});
      mockedApi.get.mockRejectedValueOnce(new Error("Network error"));

      await store.fetchSessions();

      expect(consoleSpy).toHaveBeenCalled();
      expect(store.isLoading).toBe(false);
      consoleSpy.mockRestore();
    });
  });

  describe("createSession", () => {
    it("should return created session on success", async () => {
      const store = useChatStore();
      const mockSession: Session = {
        session_id: 1,
        title: "New Conversation",
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
      };
      mockedApi.post.mockResolvedValueOnce({
        data: { data: mockSession },
      } as any);

      const result = await store.createSession();

      expect(result).toEqual(mockSession);
    });

    it("should add session to beginning of sessions array", async () => {
      const store = useChatStore();
      const mockSession: Session = {
        session_id: 1,
        title: "New Conversation",
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
      };
      mockedApi.post.mockResolvedValueOnce({
        data: { data: mockSession },
      } as any);

      await store.createSession();

      expect(store.sessions[0]).toEqual(mockSession);
    });

    it("should use custom title when provided", async () => {
      const store = useChatStore();
      mockedApi.post.mockResolvedValueOnce({
        data: {
          data: {
            session_id: 1,
            title: "Custom Title",
            created_at: "2024-01-01",
            updated_at: "2024-01-01",
          },
        },
      } as any);

      await store.createSession("Custom Title");

      expect(mockedApi.post).toHaveBeenCalledWith("/sessions", {
        title: "Custom Title",
      });
    });

    it("should return null on error", async () => {
      const store = useChatStore();
      const consoleSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});
      mockedApi.post.mockRejectedValueOnce(new Error("Network error"));

      const result = await store.createSession();

      expect(result).toBeNull();
      consoleSpy.mockRestore();
    });
  });

  describe("loadSession", () => {
    it("should set isLoading to true while loading", async () => {
      const store = useChatStore();
      mockedApi.get.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ data: { data: {} } } as any), 100),
          ),
      );

      const promise = store.loadSession(1);
      expect(store.isLoading).toBe(true);
      await promise;
    });

    it("should set currentSession from response", async () => {
      const store = useChatStore();
      const mockSession: Session = {
        session_id: 1,
        title: "Test Session",
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
      };
      mockedApi.get
        .mockResolvedValueOnce({ data: { data: mockSession } } as any)
        .mockResolvedValueOnce({ data: { data: { queries: [] } } } as any);

      await store.loadSession(1);

      expect(store.currentSession).toEqual(mockSession);
    });

    it("should set queries from history response", async () => {
      const store = useChatStore();
      const mockQueries: Query[] = [
        {
          query_id: 1,
          query_text: "What is AI?",
          response_text: "AI is...",
          input_mode: "text",
          sources: [],
          created_at: "2024-01-01",
        },
      ];
      mockedApi.get
        .mockResolvedValueOnce({ data: { data: {} } } as any)
        .mockResolvedValueOnce({
          data: { data: { queries: mockQueries } },
        } as any);

      await store.loadSession(1);

      expect(store.queries).toEqual(mockQueries);
    });

    it("should set isLoading to false after loading", async () => {
      const store = useChatStore();
      mockedApi.get
        .mockResolvedValueOnce({ data: { data: {} } } as any)
        .mockResolvedValueOnce({ data: { data: { queries: [] } } } as any);

      await store.loadSession(1);

      expect(store.isLoading).toBe(false);
    });
  });

  describe("sendQuery", () => {
    it("should return null if no current session", async () => {
      const store = useChatStore();
      store.currentSession = null;

      const result = await store.sendQuery("Test query");

      expect(result).toBeNull();
    });

    it("should set isSending to true while sending", async () => {
      const store = useChatStore();
      store.currentSession = {
        session_id: 1,
        title: "Test",
        created_at: "",
        updated_at: "",
      };
      mockedApi.post.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ data: { data: {} } } as any), 100),
          ),
      );

      const promise = store.sendQuery("Test query");
      expect(store.isSending).toBe(true);
      await promise;
    });

    it("should add query to queries array on success", async () => {
      const store = useChatStore();
      store.currentSession = {
        session_id: 1,
        title: "Test",
        created_at: "",
        updated_at: "",
      };
      const mockQuery: Query = {
        query_id: 1,
        query_text: "What is AI?",
        response_text: "AI is...",
        input_mode: "text",
        sources: [],
        created_at: "2024-01-01",
      };
      mockedApi.post.mockResolvedValueOnce({
        data: { data: mockQuery },
      } as any);

      await store.sendQuery("What is AI?");

      expect(store.queries).toContainEqual(mockQuery);
    });

    it("should update session title on first query", async () => {
      const store = useChatStore();
      store.currentSession = {
        session_id: 1,
        title: "New Conversation",
        created_at: "",
        updated_at: "",
      };
      store.sessions = [
        {
          session_id: 1,
          title: "New Conversation",
          created_at: "",
          updated_at: "",
        },
      ];
      store.queries = [];
      const mockQuery: Query = {
        query_id: 1,
        query_text: "What is AI?",
        response_text: "AI is...",
        input_mode: "text",
        sources: [],
        created_at: "2024-01-01",
      };
      mockedApi.post.mockResolvedValueOnce({
        data: { data: mockQuery },
      } as any);

      await store.sendQuery("What is AI?");

      expect(store.currentSession?.title).toBe("What is AI?");
    });

    it("should truncate long query text for title", async () => {
      const store = useChatStore();
      store.currentSession = {
        session_id: 1,
        title: "New Conversation",
        created_at: "",
        updated_at: "",
      };
      store.sessions = [
        {
          session_id: 1,
          title: "New Conversation",
          created_at: "",
          updated_at: "",
        },
      ];
      store.queries = [];
      const longQuery =
        "This is a very long query that exceeds fifty characters and should be truncated";
      const mockQuery: Query = {
        query_id: 1,
        query_text: longQuery,
        response_text: "Response...",
        input_mode: "text",
        sources: [],
        created_at: "2024-01-01",
      };
      mockedApi.post.mockResolvedValueOnce({
        data: { data: mockQuery },
      } as any);

      await store.sendQuery(longQuery);

      expect(store.currentSession?.title).toBe(
        longQuery.substring(0, 50) + "...",
      );
    });

    it("should use voice input mode when specified", async () => {
      const store = useChatStore();
      store.currentSession = {
        session_id: 1,
        title: "Test",
        created_at: "",
        updated_at: "",
      };
      mockedApi.post.mockResolvedValueOnce({ data: { data: {} } } as any);

      await store.sendQuery("Test query", "voice");

      expect(mockedApi.post).toHaveBeenCalledWith("/query", {
        session_id: 1,
        query_text: "Test query",
        input_mode: "voice",
      });
    });

    it("should set isSending to false after sending", async () => {
      const store = useChatStore();
      store.currentSession = {
        session_id: 1,
        title: "Test",
        created_at: "",
        updated_at: "",
      };
      mockedApi.post.mockResolvedValueOnce({ data: { data: {} } } as any);

      await store.sendQuery("Test query");

      expect(store.isSending).toBe(false);
    });

    it("should return null on error", async () => {
      const store = useChatStore();
      store.currentSession = {
        session_id: 1,
        title: "Test",
        created_at: "",
        updated_at: "",
      };
      const consoleSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});
      mockedApi.post.mockRejectedValueOnce(new Error("Network error"));

      const result = await store.sendQuery("Test query");

      expect(result).toBeNull();
      consoleSpy.mockRestore();
    });
  });

  describe("deleteSession", () => {
    it("should remove session from sessions array", async () => {
      const store = useChatStore();
      store.sessions = [
        { session_id: 1, title: "Session 1", created_at: "", updated_at: "" },
        { session_id: 2, title: "Session 2", created_at: "", updated_at: "" },
      ];
      mockedApi.delete.mockResolvedValueOnce({} as any);

      await store.deleteSession(1);

      expect(store.sessions).toHaveLength(1);
      expect(store.sessions[0]?.session_id).toBe(2);
    });

    it("should clear currentSession if deleted session was active", async () => {
      const store = useChatStore();
      store.sessions = [
        { session_id: 1, title: "Session 1", created_at: "", updated_at: "" },
      ];
      store.currentSession = {
        session_id: 1,
        title: "Session 1",
        created_at: "",
        updated_at: "",
      };
      store.queries = [
        {
          query_id: 1,
          query_text: "Test",
          response_text: "Response",
          input_mode: "text",
          sources: [],
          created_at: "",
        },
      ];
      mockedApi.delete.mockResolvedValueOnce({} as any);

      await store.deleteSession(1);

      expect(store.currentSession).toBeNull();
      expect(store.queries).toEqual([]);
    });

    it("should not clear currentSession if different session was deleted", async () => {
      const store = useChatStore();
      store.sessions = [
        { session_id: 1, title: "Session 1", created_at: "", updated_at: "" },
        { session_id: 2, title: "Session 2", created_at: "", updated_at: "" },
      ];
      store.currentSession = {
        session_id: 2,
        title: "Session 2",
        created_at: "",
        updated_at: "",
      };
      mockedApi.delete.mockResolvedValueOnce({} as any);

      await store.deleteSession(1);

      expect(store.currentSession?.session_id).toBe(2);
    });
  });

  describe("clearCurrentSession", () => {
    it("should set currentSession to null", () => {
      const store = useChatStore();
      store.currentSession = {
        session_id: 1,
        title: "Test",
        created_at: "",
        updated_at: "",
      };

      store.clearCurrentSession();

      expect(store.currentSession).toBeNull();
    });

    it("should clear queries array", () => {
      const store = useChatStore();
      store.queries = [
        {
          query_id: 1,
          query_text: "Test",
          response_text: "Response",
          input_mode: "text",
          sources: [],
          created_at: "",
        },
      ];

      store.clearCurrentSession();

      expect(store.queries).toEqual([]);
    });
  });
});
