<script setup lang="ts">
import { ref, watch, nextTick, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore, type Query } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import { useVoice } from '@/composables/useVoice'

const MAX_QUERY_LENGTH = 2000

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()
const authStore = useAuthStore()
const voice = useVoice()

const messageInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

// Character count validation
const charCount = computed(() => messageInput.value.length)
const isOverLimit = computed(() => charCount.value > MAX_QUERY_LENGTH)
const charCountClass = computed(() => {
    if (isOverLimit.value) return 'text-red-500'
    if (charCount.value > MAX_QUERY_LENGTH * 0.9) return 'text-yellow-500'
    return 'text-[var(--text-secondary)]'
})

// Load sessions on mount
onMounted(async () => {
    await chatStore.fetchSessions()

    const sessionId = route.params.sessionId as string
    if (sessionId) {
        await chatStore.loadSession(parseInt(sessionId))
    }
})

// Watch for route changes
watch(
    () => route.params.sessionId,
    async (newId) => {
        // Stop any playing audio when switching sessions
        voice.stopSpeaking()

        if (newId) {
            await chatStore.loadSession(parseInt(newId as string))
        } else {
            chatStore.clearCurrentSession()
        }
    }
)

// Auto-scroll to bottom when new messages arrive
watch(
    () => chatStore.queries.length,
    async () => {
        await nextTick()
        if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
    }
)

// Watch voice transcript and populate input
watch(
    () => voice.transcript.value,
    (newTranscript) => {
        if (newTranscript) {
            messageInput.value = newTranscript
        }
    }
)

// Voice input no longer auto-submits - user can edit before sending
// The transcript is placed in the input field for review

async function createNewSession() {
    const session = await chatStore.createSession()
    if (session) {
        router.push({ name: 'chat-session', params: { sessionId: session.session_id } })
    }
}

async function selectSession(sessionId: number) {
    router.push({ name: 'chat-session', params: { sessionId } })
}

async function sendMessage(inputMode: 'text' | 'voice' = 'text') {
    const text = messageInput.value.trim()
    if (!text || chatStore.isSending || isOverLimit.value) return

    // Create a session if we don't have one
    if (!chatStore.currentSession) {
        const session = await chatStore.createSession()
        if (session) {
            await router.push({ name: 'chat-session', params: { sessionId: session.session_id } })
            await chatStore.loadSession(session.session_id)
        }
    }

    messageInput.value = ''
    const result = await chatStore.sendQuery(text, inputMode)

    // Autoplay the response audio
    if (result && voice.hasSpeechSynthesis) {
        await voice.speak(result.response_text)
    }

    inputRef.value?.focus()
}

function toggleVoiceInput() {
    if (voice.isListening.value) {
        voice.stopListening()
        // Submit if we have a transcript
        if (messageInput.value.trim()) {
            sendMessage('voice')
        }
    } else {
        // Stop any playing audio before starting to record
        voice.stopSpeaking()
        voice.startListening()
    }
}

function toggleSpeech(query: Query) {
    if (voice.isSpeaking.value) {
        voice.stopSpeaking()
    } else {
        voice.speak(query.response_text)
    }
}

// Sidebar always starts closed - user opens via hamburger menu
const showSidebar = ref(false)

function toggleSidebar() {
    showSidebar.value = !showSidebar.value
}
</script>

<template>
    <!-- Use h-full since App.vue main wrapper handles the height -->
    <div class="h-full flex bg-[var(--background)] font-sans overflow-hidden">
        <!-- Mobile Overlay Backdrop -->
        <div v-if="showSidebar" @click="showSidebar = false" class="fixed inset-0 bg-black/30 z-10 md:hidden"></div>

        <!-- Sidebar - fixed overlay that slides in from left, below navbar -->
        <aside :class="[
            'flex flex-col border-r border-[var(--border)] transition-all duration-300 bg-[var(--surface)] w-64',
            'fixed z-20 top-[57px] md:top-[65px] bottom-0',
            showSidebar ? 'left-0' : '-left-64'
        ]">
            <!-- Sidebar Header -->
            <div class="p-4 border-b border-[var(--border)]">
                <div class="flex items-center justify-between mb-3">
                    <span class="font-serif text-sm text-[var(--text-secondary)]">History</span>
                    <button @click="showSidebar = false"
                        class="p-1 hover:bg-[var(--surface-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors rounded">
                        <span class="text-lg">✕</span>
                    </button>
                </div>
                <button @click="createNewSession"
                    class="w-full py-2 px-3 border border-[var(--primary)] text-[var(--primary)] hover:bg-[var(--primary)] hover:text-white font-serif transition-colors flex items-center justify-center gap-2 text-sm rounded">
                    <span>+</span>
                    <span>New Research</span>
                </button>
            </div>

            <!-- Sessions List -->
            <div class="flex-1 overflow-y-auto p-3">
                <div v-if="chatStore.isLoading && chatStore.sessions.length === 0"
                    class="p-3 text-center text-[var(--text-secondary)] italic font-serif text-sm">
                    Retrieving archives...
                </div>
                <div v-else-if="chatStore.sessions.length === 0"
                    class="p-3 text-center text-[var(--text-secondary)] italic font-serif text-sm">
                    No prior research found.
                </div>
                <button v-for="session in chatStore.sessions" :key="session.session_id"
                    @click="selectSession(session.session_id)" :class="[
                        'w-full text-left p-2 mb-1 transition-colors truncate font-serif text-sm border-l-2 rounded-r',
                        chatStore.currentSession?.session_id === session.session_id
                            ? 'border-[var(--primary)] bg-[var(--surface-hover)] text-[var(--text-primary)] font-medium'
                            : 'border-transparent hover:bg-[var(--surface-hover)] text-[var(--text-secondary)]'
                    ]">
                    {{ session.title }}
                </button>
            </div>

            <!-- User Info -->
            <div class="p-4 border-t border-[var(--border)]">
                <div class="flex items-center justify-between">
                    <span class="text-xs text-[var(--text-secondary)] truncate font-mono">
                        {{ authStore.email }}
                    </span>
                    <button @click="authStore.logout()"
                        class="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors uppercase tracking-wider">
                        Exit
                    </button>
                </div>
            </div>
        </aside>

        <!-- Main Chat Area - shifts right on desktop when sidebar is open -->
        <main :class="[
            'flex-1 flex flex-col bg-[var(--background)] w-full transition-all duration-300',
            showSidebar ? 'md:ml-64' : 'ml-0'
        ]">
            <!-- Header -->
            <header
                class="px-4 py-2 md:px-6 md:py-4 border-b border-[var(--border)] flex items-center gap-2 md:gap-4 shrink-0">
                <button @click="toggleSidebar"
                    class="p-2 hover:bg-[var(--surface)] text-[var(--text-secondary)] transition-colors rounded">
                    <span class="text-lg">☰</span>
                </button>
                <h1 class="flex-1 text-lg font-serif text-[var(--text-primary)] truncate">
                    {{ chatStore.currentSession?.title || 'New Research Session' }}
                </h1>
                <!-- Always visible New Chat button -->
                <button @click="createNewSession"
                    class="px-4 py-2 border border-[var(--primary)] text-[var(--primary)] hover:bg-[var(--primary)] hover:text-white text-sm font-serif transition-colors rounded flex items-center gap-2">
                    <span>+</span>
                    <span class="hidden sm:inline">New Chat</span>
                </button>
            </header>

            <!-- Messages -->
            <div ref="messagesContainer" class="flex-1 overflow-y-auto px-4 py-2 md:px-8 lg:px-12 space-y-6 min-h-0">
                <!-- Empty State -->
                <div v-if="!chatStore.currentSession || chatStore.queries.length === 0"
                    class="flex flex-col items-center justify-center text-center opacity-50 py-8">
                    <div class="text-3xl mb-2 font-serif text-[var(--text-secondary)]">W</div>
                    <h2 class="text-lg font-serif text-[var(--text-primary)] mb-1">
                        Begin Your Research
                    </h2>
                    <p class="text-sm text-[var(--text-secondary)] max-w-md leading-relaxed font-serif italic">
                        Speak or type to query the global encyclopedia.
                    </p>
                </div>

                <!-- Messages -->
                <template v-else>
                    <div v-for="query in chatStore.queries" :key="query.query_id" class="space-y-4 animate-fade-in">
                        <!-- User Message (As a Header) -->
                        <div class="max-w-3xl mx-auto border-b border-[var(--border)] pb-3">
                            <div class="flex items-center gap-2 mb-1" v-if="query.input_mode === 'voice'">
                                <span class="text-xs uppercase tracking-wide text-[var(--text-secondary)]">Voice
                                    Input</span>
                            </div>
                            <h3
                                class="text-lg md:text-xl font-serif font-semibold text-[var(--text-primary)] leading-snug">
                                {{ query.query_text }}
                            </h3>
                        </div>

                        <!-- AI Response (As Article Text) -->
                        <div class="max-w-3xl mx-auto">
                            <div
                                class="prose prose-sm max-w-none text-[var(--text-primary)] leading-relaxed font-serif">
                                <p class="whitespace-pre-wrap">{{ query.response_text }}</p>
                            </div>

                            <!-- Wikipedia Sources -->
                            <div v-if="query.sources && query.sources.length > 0"
                                class="mt-4 pt-3 border-t border-[var(--border)]">
                                <p class="text-xs uppercase tracking-wide text-[var(--text-secondary)] mb-2 font-sans">
                                    References</p>
                                <ol class="list-decimal list-inside space-y-1">
                                    <li v-for="source in query.sources" :key="source.url"
                                        class="text-sm text-[var(--text-secondary)]">
                                        <a :href="source.url" target="_blank" rel="noopener noreferrer"
                                            class="text-[var(--primary)] hover:underline hover:text-[var(--primary-hover)] transition-colors">
                                            {{ source.title }}
                                        </a>
                                    </li>
                                </ol>
                            </div>

                            <button v-if="voice.hasSpeechSynthesis" @click="toggleSpeech(query)"
                                class="mt-4 flex items-center gap-2 text-xs text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors uppercase tracking-wide">
                                {{ voice.isSpeaking.value ? '⏹ Stop' : '🔊 Read Aloud' }}
                            </button>
                        </div>
                    </div>
                </template>

                <!-- Loading -->
                <div v-if="chatStore.isSending" class="max-w-4xl mx-auto pl-0 md:pl-4 opacity-50">
                    <div class="flex items-center gap-3">
                        <div class="w-2 h-2 bg-[var(--text-secondary)] rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-[var(--text-secondary)] rounded-full animate-bounce delay-75"></div>
                        <div class="w-2 h-2 bg-[var(--text-secondary)] rounded-full animate-bounce delay-150"></div>
                        <span class="text-sm font-serif italic text-[var(--text-secondary)]">Consulting
                            archives...</span>
                    </div>
                </div>
            </div>

            <!-- Input Area -->
            <div class="p-3 pb-6 md:p-6 md:pb-8 border-t border-[var(--border)] bg-[var(--background)] shrink-0">
                <div class="max-w-4xl mx-auto">
                    <form @submit.prevent="sendMessage('text')" class="flex gap-3 items-end">
                        <!-- Voice Button -->
                        <button v-if="voice.hasSpeechRecognition" type="button" @click="toggleVoiceInput" :class="[
                            'p-3 rounded border transition-all',
                            voice.isListening.value
                                ? 'bg-red-500 border-red-500 text-white animate-pulse'
                                : 'border-[var(--border)] hover:border-[var(--primary)] bg-transparent text-[var(--text-secondary)]'
                        ]" :title="voice.isListening.value ? 'Stop & send' : 'Start voice input'">
                            <span class="text-lg">{{ voice.isListening.value ? '⏹' : '🎤' }}</span>
                        </button>

                        <div class="flex-1 relative">
                            <input ref="inputRef" v-model="messageInput" type="text"
                                :placeholder="voice.isListening.value ? 'Listening...' : 'Start your research here...'"
                                :disabled="chatStore.isSending" :maxlength="MAX_QUERY_LENGTH + 100" :class="[
                                    'w-full px-3 py-2 md:px-4 md:py-3 bg-transparent border-b-2 text-base font-serif text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none disabled:opacity-50 transition-colors',
                                    isOverLimit ? 'border-red-500' : 'border-[var(--border)] focus:border-[var(--primary)]'
                                ]" />
                            <span :class="['absolute right-0 top-full mt-1 text-xs font-mono', charCountClass]">
                                {{ charCount }}/{{ MAX_QUERY_LENGTH }}
                            </span>
                        </div>

                        <!-- Send Button -->
                        <button type="submit" :disabled="!messageInput.trim() || chatStore.isSending || isOverLimit"
                            class="px-4 py-2 md:px-6 md:py-3 bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-serif text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-wider rounded">
                            Query
                        </button>
                    </form>

                    <!-- Character limit warning -->
                    <div v-if="isOverLimit" class="mt-3 text-center text-sm text-red-500 font-serif">
                        Query exceeds maximum length
                    </div>

                    <!-- Voice Status - shows recording indicator -->
                    <div v-if="voice.isListening.value" class="mt-3 flex items-center justify-center gap-3">
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                            <span class="text-sm text-red-600 font-medium">Recording</span>
                        </div>
                        <span class="text-sm text-[var(--text-secondary)]">•</span>
                        <span class="text-sm text-[var(--text-secondary)]">Click stop to send</span>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>
