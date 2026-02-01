<script setup lang="ts">
import { ref } from 'vue'

interface RoadmapItem {
    id: string
    title: string
    category: 'infrastructure' | 'rag' | 'auth' | 'ux' | 'integration' | 'ai'
    priority: 'high' | 'medium' | 'low'
    effort: 'small' | 'medium' | 'large'
    description: string
    details: string[]
    expanded: boolean
}

const categories = [
    { id: 'all', label: 'All', color: '' },
    { id: 'infrastructure', label: 'Infrastructure', color: 'bg-purple-100 text-purple-800' },
    { id: 'rag', label: 'RAG & AI', color: 'bg-blue-100 text-blue-800' },
    { id: 'auth', label: 'Authentication', color: 'bg-green-100 text-green-800' },
    { id: 'ux', label: 'UI/UX', color: 'bg-orange-100 text-orange-800' },
    { id: 'integration', label: 'Integrations', color: 'bg-pink-100 text-pink-800' },
    { id: 'ai', label: 'Advanced AI', color: 'bg-cyan-100 text-cyan-800' },
]

const selectedCategory = ref('all')

const roadmapItems = ref<RoadmapItem[]>([
    {
        id: '1',
        title: 'Complete CI/CD Pipeline',
        category: 'infrastructure',
        priority: 'high',
        effort: 'medium',
        description: 'The current CI/CD pipeline is incomplete and not working to its full potential.',
        details: [
            'Implement end-to-end automated testing in pipeline',
            'Add staging environment with automatic deployment on PR merge',
            'Implement blue-green or canary deployments for zero-downtime updates',
            'Add automated rollback on deployment failure',
            'Add DAST (Dynamic Application Security Testing) to complement existing Bandit SAST',
            'Add performance regression testing',
        ],
        expanded: false,
    },
    {
        id: '2',
        title: 'Infrastructure as Code in CI/CD',
        category: 'infrastructure',
        priority: 'high',
        effort: 'medium',
        description: 'Terraform infrastructure changes should be fully automated through CI/CD.',
        details: [
            'Automated Terraform plan on every PR with comment summary',
            'Protected apply workflow requiring approvals',
            'Drift detection to catch manual changes',
            'Terraform state locking and remote backend improvements',
        ],
        expanded: false,
    },
    {
        id: '3',
        title: 'Observability & Cost Optimization',
        category: 'infrastructure',
        priority: 'medium',
        effort: 'medium',
        description: 'Enhance monitoring, error tracking, and optimize cloud costs.',
        details: [
            'Integrate Sentry for error tracking and alerting',
            'Set up Grafana dashboards for application metrics and logs',
            'Configure CloudWatch alarms for key performance indicators',
            'Add horizontal autoscaling based on custom metrics (latency, queue depth)',
            'Implement circuit breakers for external API calls (Wikipedia, OpenAI)',
        ],
        expanded: false,
    },

    {
        id: '4',
        title: 'OpenAI Whisper for Voice Transcription',
        category: 'rag',
        priority: 'high',
        effort: 'medium',
        description: 'Replace browser Speech Recognition API with OpenAI Whisper for superior transcription accuracy.',
        details: [
            'Implement audio recording in the browser (MediaRecorder API)',
            'Stream audio to backend for Whisper processing',
            'Support multiple languages with automatic detection',
            'Handle noisy environments and accents better',
            'Reduce latency with streaming transcription',
            'Fall back to browser API when offline',
        ],
        expanded: false,
    },
    {
        id: '5',
        title: 'Enhanced Document Retrieval',
        category: 'rag',
        priority: 'high',
        effort: 'large',
        description: 'Improve the RAG pipeline to retrieve and synthesize from more documents.',
        details: [
            'Implement semantic search with vector embeddings',
            'Add document chunking strategies for better context windows',
            'Implement re-ranking of retrieved documents',
            'Cache frequently accessed Wikipedia articles',
            'Add hybrid search combining keyword + semantic matching',
            'Implement query expansion and reformulation',
        ],
        expanded: false,
    },
    {
        id: '6',
        title: 'Multi-Source Knowledge Base',
        category: 'rag',
        priority: 'medium',
        effort: 'large',
        description: 'Expand beyond Wikipedia to include additional authoritative sources.',
        details: [
            'Add arXiv for scientific papers',
            'Include Wikidata for structured facts',
            'Add news sources for current events (with recency weighting)',
            'Include open-access textbooks and educational resources',
            'Implement source reliability scoring',
            'Add citation cross-referencing',
        ],
        expanded: false,
    },
    {
        id: '7',
        title: 'Response Quality Evaluation',
        category: 'rag',
        priority: 'medium',
        effort: 'medium',
        description: 'Implement automated evaluation of RAG response quality.',
        details: [
            'Add factuality checking against source documents',
            'Implement hallucination detection',
            'Track citation accuracy and coverage',
            'A/B testing framework for prompt variations',
            'User feedback collection and analysis',
            'Automated regression testing with golden datasets',
        ],
        expanded: false,
    },

    {
        id: '8',
        title: 'Email Verification Flow',
        category: 'auth',
        priority: 'high',
        effort: 'small',
        description: 'Implement email verification for new user registrations.',
        details: [
            'Send verification email on registration via Stytch',
            'Verification link with secure token',
            'Resend verification email functionality',
            'Account activation required before full access',
            'Email change verification flow',
        ],
        expanded: false,
    },
    {
        id: '9',
        title: 'OAuth Social Login',
        category: 'auth',
        priority: 'low',
        effort: 'medium',
        description: 'Allow users to sign in with social accounts.',
        details: [
            'Google OAuth integration',
            'GitHub OAuth for developers',
            'Apple Sign-In for iOS users',
        ],
        expanded: false,
    },

    // UI/UX Improvements
    {
        id: '10',
        title: 'Conversational UI Enhancements',
        category: 'ux',
        priority: 'high',
        effort: 'medium',
        description: 'Improve the chat interface for better user experience.',
        details: [
            'Markdown rendering in responses with code blocks',
            'Inline Wikipedia article previews',
            'Collapsible source citations',
            'Message reactions and bookmarking',
            'Share conversation feature',
            'Export conversation as PDF/Markdown',
        ],
        expanded: false,
    },
    {
        id: '11',
        title: 'Contextual Personalization',
        category: 'ai',
        priority: 'medium',
        effort: 'large',
        description: "Use user context to provide more relevant and personalized responses.",
        details: [
            'Location-aware responses (local Wikipedia articles, nearby landmarks)',
            'Time-aware context (current events, seasonal topics)',
            'Learning from user query history for better relevance',
            'Interest profiling for proactive suggestions',
            'Language preference detection and auto-translation',
            'Difficulty level adjustment based on user expertise',
        ],
        expanded: false,
    },
    {
        id: '12',
        title: 'Named Entity Recognition (NER)',
        category: 'ai',
        priority: 'medium',
        effort: 'medium',
        description: 'Implement dedicated entity recognition for better query understanding.',
        details: [
            'Extract people, places, organizations, dates from queries',
            'Link entities to Wikipedia/Wikidata entries',
            'Disambiguation for entities with multiple meanings',
            'Entity relationship mapping',
            'Timeline generation for historical entities',
            'Knowledge graph visualization',
        ],
        expanded: false,
    },
    {
        id: '13',
        title: 'Multi-Modal Responses',
        category: 'ai',
        priority: 'low',
        effort: 'large',
        description: 'Enhance responses with images, diagrams, and interactive elements.',
        details: [
            'Include relevant Wikipedia images in responses',
            'Generate diagrams for complex explanations',
            'Interactive maps for geographical queries',
            'Timeline visualizations for historical topics',
            'Equation rendering for mathematical content',
            'Audio clips for pronunciation and music topics',
        ],
        expanded: false,
    },
    {
        id: '14',
        title: 'Browser Extension',
        category: 'integration',
        priority: 'low',
        effort: 'large',
        description: 'Create a browser extension for quick access to WikiVoice.',
        details: [
            'Highlight text and query WikiVoice',
            'Voice input from any webpage',
            'Quick definitions and summaries',
            'Save to conversation history',
            'Cross-browser support (Chrome, Firefox, Safari)',
        ],
        expanded: false,
    },
])

function toggleItem(id: string) {
    const item = roadmapItems.value.find(i => i.id === id)
    if (item) {
        item.expanded = !item.expanded
    }
}

function getCategoryColor(category: string) {
    return categories.find(c => c.id === category)?.color || ''
}

function getPriorityColor(priority: string) {
    switch (priority) {
        case 'high': return 'bg-red-100 text-red-800'
        case 'medium': return 'bg-yellow-100 text-yellow-800'
        case 'low': return 'bg-gray-100 text-gray-800'
        default: return ''
    }
}

function getEffortBadge(effort: string) {
    switch (effort) {
        case 'small': return '⚡ Small'
        case 'medium': return '🔧 Medium'
        case 'large': return '🏗️ Large'
        default: return effort
    }
}

const filteredItems = computed(() => {
    if (selectedCategory.value === 'all') {
        return roadmapItems.value
    }
    return roadmapItems.value.filter(item => item.category === selectedCategory.value)
})

import { computed } from 'vue'
</script>

<template>
    <div class="min-h-screen bg-[var(--background)] font-sans">
        <!-- Header -->
        <div class="border-b border-[var(--border)] bg-[var(--surface)]">
            <div class="max-w-6xl mx-auto px-4 md:px-8 py-8">
                <h1 class="text-3xl md:text-4xl font-serif font-bold text-[var(--text-primary)] mb-2">
                    WikiVoice Future Roadmap
                </h1>
                <p class="text-[var(--text-secondary)] text-lg">
                    Planned improvements and features for the next generation of WikiVoice
                </p>
            </div>
        </div>

        <div class="max-w-6xl mx-auto px-4 md:px-8 py-8">
            <!-- Introduction -->
            <div class="prose max-w-none mb-8">
                <p class="text-[var(--text-primary)] text-lg leading-relaxed">
                    WikiVoice is an evolving platform with ambitious goals. This roadmap outlines our vision for
                    scaling the system, enhancing the AI capabilities, improving user experience, and expanding
                    integrations. Items are prioritized by impact and marked with estimated effort levels.
                </p>
            </div>

            <!-- Category Filter -->
            <div class="flex flex-wrap gap-2 mb-8">
                <button v-for="cat in categories" :key="cat.id" @click="selectedCategory = cat.id" :class="[
                    'px-4 py-2 rounded-full text-sm font-medium transition-all',
                    selectedCategory === cat.id
                        ? 'bg-[var(--primary)] text-white'
                        : 'bg-[var(--surface)] text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]'
                ]">
                    {{ cat.label }}
                </button>
            </div>

            <!-- Legend -->
            <div class="flex flex-wrap gap-4 mb-8 text-sm">
                <div class="flex items-center gap-2">
                    <span class="font-semibold text-[var(--text-secondary)]">Priority:</span>
                    <span class="px-2 py-1 rounded bg-red-100 text-red-800">High</span>
                    <span class="px-2 py-1 rounded bg-yellow-100 text-yellow-800">Medium</span>
                    <span class="px-2 py-1 rounded bg-gray-100 text-gray-800">Low</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="font-semibold text-[var(--text-secondary)]">Effort:</span>
                    <span>⚡ Small</span>
                    <span>🔧 Medium</span>
                    <span>🏗️ Large</span>
                </div>
            </div>

            <!-- Roadmap Items -->
            <div class="space-y-4">
                <TransitionGroup name="list">
                    <div v-for="item in filteredItems" :key="item.id"
                        class="border border-[var(--border)] rounded-lg overflow-hidden bg-white hover:shadow-md transition-shadow">
                        <button @click="toggleItem(item.id)"
                            class="w-full px-6 py-4 flex items-start justify-between text-left gap-4">
                            <div class="flex-1 min-w-0">
                                <div class="flex flex-wrap items-center gap-2 mb-2">
                                    <span
                                        :class="['px-2 py-0.5 rounded text-xs font-medium', getCategoryColor(item.category)]">
                                        {{categories.find(c => c.id === item.category)?.label}}
                                    </span>
                                    <span
                                        :class="['px-2 py-0.5 rounded text-xs font-medium', getPriorityColor(item.priority)]">
                                        {{ item.priority.charAt(0).toUpperCase() + item.priority.slice(1) }} Priority
                                    </span>
                                    <span class="text-xs text-[var(--text-secondary)]">
                                        {{ getEffortBadge(item.effort) }}
                                    </span>
                                </div>
                                <h3 class="text-lg font-serif font-bold text-[var(--text-primary)] mb-1">
                                    {{ item.title }}
                                </h3>
                                <p class="text-sm text-[var(--text-secondary)]">
                                    {{ item.description }}
                                </p>
                            </div>
                            <span class="text-[var(--text-secondary)] text-xl flex-shrink-0">
                                {{ item.expanded ? '−' : '+' }}
                            </span>
                        </button>

                        <Transition name="expand">
                            <div v-if="item.expanded"
                                class="px-6 pb-4 border-t border-[var(--border)] bg-[var(--surface)]">
                                <ul class="mt-4 space-y-2 list-disc list-inside pl-2">
                                    <li v-for="(detail, idx) in item.details" :key="idx"
                                        class="text-sm text-[var(--text-primary)] marker:text-[var(--primary)]">
                                        {{ detail }}
                                    </li>
                                </ul>
                            </div>
                        </Transition>
                    </div>
                </TransitionGroup>
            </div>

            <!-- Summary Statistics -->
            <div class="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-6 text-center">
                    <div class="text-3xl font-bold text-[var(--primary)]">{{ roadmapItems.length }}</div>
                    <div class="text-sm text-[var(--text-secondary)]">Total Items</div>
                </div>
                <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-6 text-center">
                    <div class="text-3xl font-bold text-red-600">
                        {{roadmapItems.filter(i => i.priority === 'high').length}}
                    </div>
                    <div class="text-sm text-[var(--text-secondary)]">High Priority</div>
                </div>
                <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-6 text-center">
                    <div class="text-3xl font-bold text-green-600">
                        {{roadmapItems.filter(i => i.effort === 'small').length}}
                    </div>
                    <div class="text-sm text-[var(--text-secondary)]">Quick Wins</div>
                </div>
                <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-6 text-center">
                    <div class="text-3xl font-bold text-purple-600">
                        {{ categories.length - 1 }}
                    </div>
                    <div class="text-sm text-[var(--text-secondary)]">Categories</div>
                </div>
            </div>



        </div>
    </div>
</template>

<style scoped>
.list-enter-active,
.list-leave-active {
    transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

.expand-enter-active,
.expand-leave-active {
    transition: all 0.2s ease;
}

.expand-enter-from,
.expand-leave-to {
    opacity: 0;
    max-height: 0;
}
</style>
