/**
 * Tests for useVoice composable behavior.
 *
 * Note: These tests focus on the composable's logic rather than browser API mocking,
 * since SpeechRecognition and SpeechSynthesis are complex browser APIs.
 */
import { describe, expect, it, vi, beforeEach } from "vitest";

describe("useVoice Composable", () => {
  beforeEach(() => {
    vi.resetModules();
  });

  describe("Browser Support Detection", () => {
    it("should report no SpeechRecognition support when API is unavailable", async () => {
      // Ensure APIs are not available
      delete (globalThis as any).SpeechRecognition;
      delete (globalThis as any).webkitSpeechRecognition;
      delete (globalThis as any).speechSynthesis;

      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      expect(voice.hasSpeechRecognition).toBe(false);
    });

    it("should report no SpeechSynthesis support when API is unavailable", async () => {
      delete (globalThis as any).SpeechRecognition;
      delete (globalThis as any).webkitSpeechRecognition;
      delete (globalThis as any).speechSynthesis;

      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      expect(voice.hasSpeechSynthesis).toBe(false);
    });
  });

  describe("Initial State (without browser APIs)", () => {
    beforeEach(() => {
      delete (globalThis as any).SpeechRecognition;
      delete (globalThis as any).webkitSpeechRecognition;
      delete (globalThis as any).speechSynthesis;
    });

    it("should not be listening initially", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      expect(voice.isListening.value).toBe(false);
    });

    it("should not be speaking initially", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      expect(voice.isSpeaking.value).toBe(false);
    });

    it("should have empty transcript initially", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      expect(voice.transcript.value).toBe("");
    });

    it("should have no error initially", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      expect(voice.error.value).toBeNull();
    });
  });

  describe("startListening (without browser APIs)", () => {
    beforeEach(() => {
      delete (globalThis as any).SpeechRecognition;
      delete (globalThis as any).webkitSpeechRecognition;
      delete (globalThis as any).speechSynthesis;
    });

    it("should set error when recognition is not supported", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      voice.startListening();

      expect(voice.error.value).toContain("not supported");
    });

    it("should not change isListening when recognition is not supported", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      voice.startListening();

      expect(voice.isListening.value).toBe(false);
    });
  });

  describe("stopListening (without browser APIs)", () => {
    beforeEach(() => {
      delete (globalThis as any).SpeechRecognition;
      delete (globalThis as any).webkitSpeechRecognition;
      delete (globalThis as any).speechSynthesis;
    });

    it("should not throw when called without recognition", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      expect(() => voice.stopListening()).not.toThrow();
    });
  });

  describe("speak (without browser APIs)", () => {
    beforeEach(() => {
      delete (globalThis as any).SpeechRecognition;
      delete (globalThis as any).webkitSpeechRecognition;
      delete (globalThis as any).speechSynthesis;
    });

    it("should reject when synthesis is not supported", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      await expect(voice.speak("Hello")).rejects.toThrow("not supported");
    });

    it("should set error when synthesis is not supported", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      try {
        await voice.speak("Hello");
      } catch {
        // Expected to throw
      }

      expect(voice.error.value).toContain("not supported");
    });
  });

  describe("stopSpeaking (without browser APIs)", () => {
    beforeEach(() => {
      delete (globalThis as any).SpeechRecognition;
      delete (globalThis as any).webkitSpeechRecognition;
      delete (globalThis as any).speechSynthesis;
    });

    it("should not throw when called without synthesis", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      expect(() => voice.stopSpeaking()).not.toThrow();
    });
  });

  describe("Exported API", () => {
    beforeEach(() => {
      delete (globalThis as any).SpeechRecognition;
      delete (globalThis as any).webkitSpeechRecognition;
      delete (globalThis as any).speechSynthesis;
    });

    it("should expose all expected properties and methods", async () => {
      const { useVoice } = await import("./useVoice");
      const voice = useVoice();

      // State
      expect(voice).toHaveProperty("isListening");
      expect(voice).toHaveProperty("isSpeaking");
      expect(voice).toHaveProperty("transcript");
      expect(voice).toHaveProperty("error");

      // Capabilities
      expect(voice).toHaveProperty("hasSpeechRecognition");
      expect(voice).toHaveProperty("hasSpeechSynthesis");

      // Actions
      expect(voice).toHaveProperty("startListening");
      expect(voice).toHaveProperty("stopListening");
      expect(voice).toHaveProperty("speak");
      expect(voice).toHaveProperty("stopSpeaking");

      // Verify types
      expect(typeof voice.startListening).toBe("function");
      expect(typeof voice.stopListening).toBe("function");
      expect(typeof voice.speak).toBe("function");
      expect(typeof voice.stopSpeaking).toBe("function");
    });
  });
});
