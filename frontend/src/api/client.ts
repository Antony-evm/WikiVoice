import axios from "axios";
import { useAuthStore } from "@/stores/auth";

const api = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Send cookies automatically
});

// Response interceptor - handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore();
      authStore.logout();
    }
    return Promise.reject(error);
  },
);

/**
 * Extract error message from API response.
 * Handles both FastAPI's {detail: string} and our custom {message: string} formats.
 */
export function getErrorMessage(
  error: unknown,
  fallback = "An error occurred",
): string {
  if (axios.isAxiosError(error) && error.response?.data) {
    const data = error.response.data;
    // Our custom format: { error: string, message: string }
    if (data.message) return data.message;
    // FastAPI default format: { detail: string }
    if (data.detail) return data.detail;
    // Validation errors: { detail: [{ msg: string }] }
    if (Array.isArray(data.detail) && data.detail[0]?.msg) {
      return data.detail.map((e: { msg: string }) => e.msg).join(", ");
    }
  }
  return fallback;
}

export default api;
