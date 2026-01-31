import { ref, onUnmounted } from "vue";

export function useVoice() {
  const isListening = ref(false);
  const isSpeaking = ref(false);
  const transcript = ref("");
  const error = ref<string | null>(null);
  const voicesLoaded = ref(false);

  let recognition: SpeechRecognition | null = null;
  let synthesis: SpeechSynthesis | null = null;
  let availableVoices: SpeechSynthesisVoice[] = [];

  // Check browser support
  const SpeechRecognition =
    window.SpeechRecognition || (window as any).webkitSpeechRecognition;
  const hasSpeechRecognition = !!SpeechRecognition;
  const hasSpeechSynthesis = "speechSynthesis" in window;

  // Load voices - Chrome requires waiting for voiceschanged event
  function loadVoices() {
    if (synthesis) {
      availableVoices = synthesis.getVoices();
      voicesLoaded.value = availableVoices.length > 0;
    }
  }

  if (hasSpeechSynthesis) {
    synthesis = window.speechSynthesis;
    // Load voices immediately (works in Firefox/Safari)
    loadVoices();
    // Also listen for voiceschanged (required for Chrome)
    if (synthesis.onvoiceschanged !== undefined) {
      synthesis.addEventListener("voiceschanged", loadVoices);
    }
  }

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      isListening.value = true;
      error.value = null;
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const results = event.results;
      const lastResult = results[results.length - 1];
      if (lastResult && lastResult[0]) {
        transcript.value = lastResult[0].transcript;
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      error.value = `Speech recognition error: ${event.error}`;
      isListening.value = false;
    };

    recognition.onend = () => {
      isListening.value = false;
    };
  }

  function startListening() {
    if (!recognition) {
      error.value = "Speech recognition is not supported in this browser";
      return;
    }

    transcript.value = "";
    recognition.start();
  }

  function stopListening() {
    if (recognition && isListening.value) {
      recognition.stop();
    }
  }

  function speak(text: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!synthesis) {
        error.value = "Speech synthesis is not supported in this browser";
        reject(new Error("Speech synthesis not supported"));
        return;
      }

      // Cancel any ongoing speech
      synthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.volume = 1;

      // Try to use a natural-sounding English voice
      if (availableVoices.length > 0) {
        const preferredVoice = availableVoices.find(
          (v) =>
            v.lang.startsWith("en") &&
            (v.name.includes("Google") ||
              v.name.includes("Natural") ||
              v.name.includes("Microsoft")),
        );
        if (preferredVoice) {
          utterance.voice = preferredVoice;
        } else {
          // Fallback to first English voice
          const englishVoice = availableVoices.find((v) =>
            v.lang.startsWith("en"),
          );
          if (englishVoice) {
            utterance.voice = englishVoice;
          }
        }
      }

      utterance.onstart = () => {
        isSpeaking.value = true;
      };

      utterance.onend = () => {
        isSpeaking.value = false;
        resolve();
      };

      utterance.onerror = (event) => {
        isSpeaking.value = false;
        error.value = `Speech synthesis error: ${event.error}`;
        reject(new Error(event.error));
      };

      // Chrome bug workaround: resume synthesis if it's paused
      if (synthesis.paused) {
        synthesis.resume();
      }

      synthesis.speak(utterance);
    });
  }

  function stopSpeaking() {
    if (synthesis) {
      synthesis.cancel();
      isSpeaking.value = false;
    }
  }

  onUnmounted(() => {
    stopListening();
    stopSpeaking();
  });

  return {
    // State
    isListening,
    isSpeaking,
    transcript,
    error,
    // Capabilities
    hasSpeechRecognition,
    hasSpeechSynthesis,
    // Actions
    startListening,
    stopListening,
    speak,
    stopSpeaking,
  };
}
