/**
 * Stytch SDK configuration for secure token management.
 *
 * The Stytch JavaScript SDK provides:
 * - Automatic token storage in secure httpOnly-like storage
 * - Automatic token refresh before expiration
 * - Session management with proper security practices
 *
 * Note: Stytch headless SDK is used since we have our own UI.
 */

import { StytchHeadlessClient } from "@stytch/vanilla-js/headless";

// Get public token from environment
const publicToken = import.meta.env.VITE_STYTCH_PUBLIC_TOKEN;

if (!publicToken) {
  console.warn(
    "VITE_STYTCH_PUBLIC_TOKEN not set. Stytch SDK will not initialize properly.",
  );
}

/**
 * Initialize the Stytch headless client.
 * This client handles secure token storage and automatic refresh.
 */
export const stytchClient = new StytchHeadlessClient(publicToken || "");

/**
 * Get the current session from Stytch SDK.
 * Returns null if no session exists.
 */
export function getStytchSession() {
  return stytchClient.session.getSync();
}

/**
 * Get the current user from Stytch SDK.
 * Returns null if no user is logged in.
 */
export function getStytchUser() {
  return stytchClient.user.getSync();
}

/**
 * Get session tokens for API requests.
 * The SDK manages token refresh automatically.
 */
export function getSessionTokens() {
  const tokens = stytchClient.session.getTokens();
  return {
    sessionToken: tokens?.session_token || null,
    sessionJwt: tokens?.session_jwt || null,
  };
}

/**
 * Revoke the current session (logout).
 */
export async function revokeSession() {
  try {
    await stytchClient.session.revoke();
  } catch (error) {
    console.error("Failed to revoke Stytch session:", error);
  }
}

/**
 * Authenticate with email and password via Stytch.
 * Returns session tokens on success.
 */
export async function authenticateWithPassword(
  email: string,
  password: string,
) {
  const response = await stytchClient.passwords.authenticate({
    email,
    password,
    session_duration_minutes: 60 * 24 * 30, // 30 days
  });

  return {
    sessionToken: response.session_token,
    sessionJwt: response.session_jwt,
    user: response.user,
  };
}

/**
 * Check if there's a valid session.
 */
export function hasValidSession(): boolean {
  const session = getStytchSession();
  return !!session;
}
