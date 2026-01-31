import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/api/client";

export interface Session {
  session_id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface WikipediaSource {
  title: string;
  url: string;
}

export interface Query {
  query_id: number;
  query_text: string;
  response_text: string;
  input_mode: string;
  sources: WikipediaSource[];
  created_at: string;
}

export const useChatStore = defineStore("chat", () => {
  // State
  const sessions = ref<Session[]>([]);
  const currentSession = ref<Session | null>(null);
  const queries = ref<Query[]>([]);
  const isLoading = ref(false);
  const isSending = ref(false);

  // Actions
  async function fetchSessions() {
    console.log("[ChatStore] fetchSessions() called");
    isLoading.value = true;
    try {
      const response = await api.get("/sessions");
      console.log("[ChatStore] fetchSessions response:", response.data);
      sessions.value = response.data.data.sessions;
      console.log("[ChatStore] Sessions loaded:", sessions.value.length);
    } catch (error) {
      console.error("[ChatStore] Failed to fetch sessions:", error);
    } finally {
      isLoading.value = false;
    }
  }

  async function createSession(
    title = "New Conversation",
  ): Promise<Session | null> {
    console.log("[ChatStore] createSession() called with title:", title);
    try {
      const response = await api.post("/sessions", { title });
      const session = response.data.data;
      console.log("[ChatStore] Session created:", session);
      sessions.value.unshift(session);
      return session;
    } catch (error) {
      console.error("[ChatStore] Failed to create session:", error);
      return null;
    }
  }

  async function loadSession(sessionId: number) {
    console.log("[ChatStore] loadSession() called with sessionId:", sessionId);
    isLoading.value = true;
    try {
      const [sessionRes, historyRes] = await Promise.all([
        api.get(`/sessions/${sessionId}`),
        api.get(`/query/history/${sessionId}`),
      ]);
      currentSession.value = sessionRes.data.data;
      queries.value = historyRes.data.data.queries;
      console.log("[ChatStore] Session loaded:", currentSession.value);
      console.log("[ChatStore] Queries loaded:", queries.value.length);
    } catch (error) {
      console.error("[ChatStore] Failed to load session:", error);
    } finally {
      isLoading.value = false;
    }
  }

  async function sendQuery(
    queryText: string,
    inputMode = "text",
  ): Promise<Query | null> {
    console.log("[ChatStore] sendQuery() called:", { queryText, inputMode, sessionId: currentSession.value?.session_id });
    if (!currentSession.value) {
      console.warn("[ChatStore] No current session, cannot send query");
      return null;
    }

    isSending.value = true;
    try {
      const response = await api.post("/query", {
        session_id: currentSession.value.session_id,
        query_text: queryText,
        input_mode: inputMode,
      });
      const query = response.data.data as Query;
      console.log("[ChatStore] Query response received:", query);
      queries.value = [...queries.value, query];

      // Update session title if this was the first query
      if (queries.value.length === 1) {
        const title =
          queryText.length > 50
            ? queryText.substring(0, 50) + "..."
            : queryText;
        currentSession.value.title = title;
        const sessionIndex = sessions.value.findIndex(
          (s) => s.session_id === currentSession.value!.session_id,
        );
        if (sessionIndex !== -1 && sessions.value[sessionIndex]) {
          sessions.value[sessionIndex]!.title = title;
        }
      }

      return query;
    } catch (error) {
      console.error("Failed to send query:", error);
      return null;
    } finally {
      isSending.value = false;
    }
  }

  async function deleteSession(sessionId: number) {
    try {
      await api.delete(`/sessions/${sessionId}`);
      sessions.value = sessions.value.filter((s) => s.session_id !== sessionId);
      if (currentSession.value?.session_id === sessionId) {
        currentSession.value = null;
        queries.value = [];
      }
    } catch (error) {
      console.error("Failed to delete session:", error);
    }
  }

  function clearCurrentSession() {
    currentSession.value = null;
    queries.value = [];
  }

  function clearAllState() {
    console.log("[ChatStore] Clearing all state (logout/user switch)");
    sessions.value = [];
    currentSession.value = null;
    queries.value = [];
    isLoading.value = false;
    isSending.value = false;
  }

  return {
    // State
    sessions,
    currentSession,
    queries,
    isLoading,
    isSending,
    // Actions
    fetchSessions,
    createSession,
    loadSession,
    sendQuery,
    deleteSession,
    clearCurrentSession,
    clearAllState,
  };
});
