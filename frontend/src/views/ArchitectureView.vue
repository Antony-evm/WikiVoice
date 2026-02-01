<script setup lang="ts">
import { ref, computed } from 'vue'

interface Section {
    id: string
    title: string
    expanded: boolean
}

const sections = ref<Section[]>([
    { id: 'overview', title: 'System Overview', expanded: true },
    { id: 'frontend', title: 'Frontend Architecture', expanded: false },
    { id: 'backend', title: 'Backend Architecture', expanded: false },
    { id: 'infrastructure', title: 'Cloud Infrastructure', expanded: false },
    { id: 'data-flow', title: 'Data Flow & RAG Pipeline', expanded: false },
    { id: 'security', title: 'Security Architecture', expanded: false },
    { id: 'cicd', title: 'CI/CD Pipeline', expanded: false },
])

// Helper to get section by id safely
function getSection(id: string): Section {
    return sections.value.find(s => s.id === id) ?? { id: '', title: '', expanded: false }
}

// Computed sections for type-safe access
const overviewSection = computed(() => getSection('overview'))
const frontendSection = computed(() => getSection('frontend'))
const backendSection = computed(() => getSection('backend'))
const infraSection = computed(() => getSection('infrastructure'))
const dataFlowSection = computed(() => getSection('data-flow'))
const securitySection = computed(() => getSection('security'))
const cicdSection = computed(() => getSection('cicd'))

function toggleSection(id: string) {
    const section = sections.value.find(s => s.id === id)
    if (section) {
        section.expanded = !section.expanded
    }
}

function expandAll() {
    sections.value.forEach(s => s.expanded = true)
}

function collapseAll() {
    sections.value.forEach(s => s.expanded = false)
}

function scrollToSection(id: string) {
    const element = document.getElementById(id)
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
        const section = sections.value.find(s => s.id === id)
        if (section) section.expanded = true
    }
}
</script>

<template>
    <div class="min-h-screen bg-[var(--background)] font-sans">
        <!-- Header -->
        <div class="border-b border-[var(--border)] bg-[var(--surface)]">
            <div class="max-w-6xl mx-auto px-4 md:px-8 py-8">
                <h1 class="text-3xl md:text-4xl font-serif font-bold text-[var(--text-primary)] mb-2">
                    WikiVoice System Architecture
                </h1>
                <p class="text-[var(--text-secondary)] text-lg">
                    From <span class="italic">WikiVoice</span>, the free voice-powered encyclopedia interface
                </p>
            </div>
        </div>

        <div class="max-w-6xl mx-auto px-4 md:px-8 py-8 flex flex-col lg:flex-row gap-8">
            <!-- Table of Contents Sidebar -->
            <aside class="lg:w-64 flex-shrink-0">
                <div class="lg:sticky lg:top-24 bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4">
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="font-serif font-bold text-[var(--text-primary)]">Contents</h2>
                        <div class="flex gap-2">
                            <button @click="expandAll" class="text-xs text-[var(--primary)] hover:underline">[expand
                                all]</button>
                            <button @click="collapseAll"
                                class="text-xs text-[var(--primary)] hover:underline">[collapse]</button>
                        </div>
                    </div>
                    <nav>
                        <ol class="list-decimal list-inside space-y-2 text-sm">
                            <li v-for="section in sections" :key="section.id">
                                <button @click="scrollToSection(section.id)"
                                    class="text-[var(--primary)] hover:underline text-left">
                                    {{ section.title }}
                                </button>
                            </li>
                        </ol>
                    </nav>
                </div>
            </aside>

            <!-- Main Content -->
            <main class="flex-1 min-w-0">
                <!-- Overview Section -->
                <section :id="overviewSection.id" class="mb-8 border-b border-[var(--border)] pb-8">
                    <button @click="toggleSection(overviewSection.id)"
                        class="w-full flex items-center justify-between text-left group">
                        <h2
                            class="text-2xl font-serif font-bold text-[var(--text-primary)] group-hover:text-[var(--primary)]">
                            1. System Overview
                        </h2>
                        <span class="text-[var(--text-secondary)] text-xl">{{ overviewSection.expanded ? '−' : '+'
                        }}</span>
                    </button>

                    <div v-show="overviewSection.expanded" class="mt-4 space-y-4">
                        <p class="text-[var(--text-primary)] leading-relaxed">
                            <strong>WikiVoice</strong> is a modern, voice-enabled research interface for Wikipedia that
                            leverages
                            Retrieval-Augmented Generation (RAG) to provide conversational, cited answers from the
                            world's largest
                            encyclopedia. The system follows a monolithic architecture deployed on AWS, utilizing a
                            Vue.js SPA for the frontend.
                        </p>

                        <!-- High-Level Architecture Diagram -->
                        <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-6 my-6">
                            <h3 class="font-serif font-bold text-lg mb-4 text-center">High-Level Architecture</h3>
                            <pre class="text-xs md:text-sm font-mono overflow-x-auto text-[var(--text-primary)]">
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │   Browser (Vue.js SPA)                                                 │ │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │ │
│  │   │  Voice Input │  │  Text Input  │  │ Audio Output │                 │ │
│  │   │ (Web Speech) │  │              │  │  (TTS API)   │                 │ │
│  │   └──────────────┘  └──────────────┘  └──────────────┘                 │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS CLOUDFRONT                                 │
│                         (CDN + SSL Termination)                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
┌──────────────────────────────┐    ┌──────────────────────────────────────────┐
│        S3 BUCKET             │    │              WAF + ALB                   │
│   (Frontend Static Assets)   │    │    (Web Application Firewall + LB)       │
└──────────────────────────────┘    └──────────────────────────────────────────┘
                                                      │
                                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 VPC                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         PRIVATE SUBNETS                                 ││
│  │  ┌──────────────────────────┐    ┌──────────────────────────┐           ││
│  │  │     ECS FARGATE          │    │      RDS POSTGRESQL      │           ││
│  │  │   ┌────────────────┐     │    │   ┌─────────────────┐    │           ││
│  │  │   │    FastAPI     │     │◄───┼───│    Database     │    │           ││
│  │  │   │    Backend     │     │    │   │   (Sessions,    │    │           ││
│  │  │   └────────────────┘     │    │   │  Users, Queries)│    │           ││
│  │  └──────────────────────────┘    └──────────────────────────┘           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                    │                                 │
                    ▼                                 ▼
┌──────────────────────────────┐    ┌──────────────────────────────────────────┐
│       EXTERNAL SERVICES      │    │          EXTERNAL APIs                   │
│  ┌────────────────────────┐  │    │  ┌────────────────┐ ┌─────────────────┐  │
│  │       Stytch           │  │    │  │  OpenAI API    │ │  Wikipedia API  │  │
│  │   (Authentication)     │  │    │  │   (GPT-4o)     │ │   (MediaWiki)   │  │
│  └────────────────────────┘  │    │  └────────────────┘ └─────────────────┘  │
└──────────────────────────────┘    └──────────────────────────────────────────┘
              </pre>
                        </div>

                        <div class="bg-blue-50 border-l-4 border-[var(--primary)] p-4 rounded-r">
                            <p class="text-sm text-[var(--text-primary)]">
                                <strong>Key Technologies:</strong> Vue.js 3, TypeScript, FastAPI, Python 3.13,
                                PostgreSQL,
                                OpenAI GPT-4o, Terraform, AWS (ECS Fargate, RDS, CloudFront, S3, WAF)
                            </p>
                        </div>
                    </div>
                </section>

                <!-- Frontend Architecture Section -->
                <section :id="frontendSection.id" class="mb-8 border-b border-[var(--border)] pb-8">
                    <button @click="toggleSection(frontendSection.id)"
                        class="w-full flex items-center justify-between text-left group">
                        <h2
                            class="text-2xl font-serif font-bold text-[var(--text-primary)] group-hover:text-[var(--primary)]">
                            2. Frontend Architecture
                        </h2>
                        <span class="text-[var(--text-secondary)] text-xl">{{ frontendSection.expanded ? '−' : '+'
                        }}</span>
                    </button>

                    <div v-show="frontendSection.expanded" class="mt-4 space-y-4">
                        <p class="text-[var(--text-primary)] leading-relaxed">
                            The frontend is a Single Page Application (SPA) built with <strong>Vue.js 3</strong> using
                            the
                            Composition API and TypeScript for type safety. It features a minimalist, Wikipedia-inspired
                            design
                            system with a research-focused aesthetic.
                        </p>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">2.1 Technology Stack
                        </h3>
                        <table class="w-full border-collapse border border-[var(--border)] text-sm mt-4">
                            <thead class="bg-[var(--surface)]">
                                <tr>
                                    <th class="border border-[var(--border)] px-4 py-2 text-left">Technology</th>
                                    <th class="border border-[var(--border)] px-4 py-2 text-left">Purpose</th>
                                    <th class="border border-[var(--border)] px-4 py-2 text-left">Version</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">Vue.js 3</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Reactive UI framework</td>
                                    <td class="border border-[var(--border)] px-4 py-2">3.x (Composition API)</td>
                                </tr>
                                <tr class="bg-[var(--surface)]">
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">TypeScript</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Static typing</td>
                                    <td class="border border-[var(--border)] px-4 py-2">5.x</td>
                                </tr>
                                <tr>
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">Vite</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Build tool & dev server</td>
                                    <td class="border border-[var(--border)] px-4 py-2">5.x</td>
                                </tr>
                                <tr class="bg-[var(--surface)]">
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">Tailwind CSS</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Utility-first styling</td>
                                    <td class="border border-[var(--border)] px-4 py-2">3.x</td>
                                </tr>
                                <tr>
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">Pinia</td>
                                    <td class="border border-[var(--border)] px-4 py-2">State management</td>
                                    <td class="border border-[var(--border)] px-4 py-2">2.x</td>
                                </tr>
                                <tr class="bg-[var(--surface)]">
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">Vue Router</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Client-side routing</td>
                                    <td class="border border-[var(--border)] px-4 py-2">4.x</td>
                                </tr>
                            </tbody>
                        </table>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">2.2 Voice Interface
                        </h3>
                        <p class="text-[var(--text-primary)] leading-relaxed">
                            The voice capabilities are implemented using the <strong>Web Speech API</strong>, which
                            provides:
                        </p>
                        <ul class="list-disc list-inside space-y-2 ml-4 text-[var(--text-primary)]">
                            <li><strong>SpeechRecognition:</strong> Converts spoken words to text for query input</li>
                            <li><strong>SpeechSynthesis:</strong> Reads responses aloud using text-to-speech</li>
                        </ul>

                        <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4 my-4">
                            <h4 class="font-mono text-sm font-bold mb-2">Voice Flow Diagram</h4>
                            <pre class="text-xs font-mono overflow-x-auto">
User Speaks → SpeechRecognition API → Transcript Text → API Request
                                                              │
User Hears  ← SpeechSynthesis API  ← Response Text  ← API Response
              </pre>
                        </div>


                    </div>
                </section>

                <!-- Backend Architecture Section -->
                <section :id="backendSection.id" class="mb-8 border-b border-[var(--border)] pb-8">
                    <button @click="toggleSection(backendSection.id)"
                        class="w-full flex items-center justify-between text-left group">
                        <h2
                            class="text-2xl font-serif font-bold text-[var(--text-primary)] group-hover:text-[var(--primary)]">
                            3. Backend Architecture
                        </h2>
                        <span class="text-[var(--text-secondary)] text-xl">{{ backendSection.expanded ? '−' : '+'
                        }}</span>
                    </button>

                    <div v-show="backendSection.expanded" class="mt-4 space-y-4">
                        <p class="text-[var(--text-primary)] leading-relaxed">
                            The backend is built with <strong>FastAPI</strong>, a modern, high-performance Python web
                            framework.
                            It follows a clean architecture pattern with clear separation between layers.
                        </p>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">3.1 Layered
                            Architecture</h3>
                        <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4 my-4">
                            <pre class="text-xs md:text-sm font-mono overflow-x-auto">
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                │
│   ┌─────────────┐  ┌─────────────┐  ┌──────────────┐            │
│   │auth_router  │  │query_router │  │session_router│            │
│   └─────────────┘  └─────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                           │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │auth_service │  │rag_service  │  │user_service │             │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│          │                │                │                    │
└──────────┼────────────────┼────────────────┼────────────────────┘
           ▲                ▲                ▲
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DOMAIN LAYER                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│   │ Entities │    │ Mappers  │    │Responses │                  │
│   └──────────┘    └──────────┘    └──────────┘                  │
└─────────────────────────────────────────────────────────────────┘
           ▲                ▲                ▲
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
│   ┌───────────────┐  ┌────────────────┐  ┌───────────────────┐  │
│   │  Repositories │  │Wikipedia Client│  │  External APIs    │  │
│   │  (PostgreSQL) │  │  (MediaWiki)   │  │ (OpenAI, Stytch)  │  │
│   └───────────────┘  └────────────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────────────────┘


              </pre>
                        </div>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">3.2 Technology Stack
                        </h3>
                        <table class="w-full border-collapse border border-[var(--border)] text-sm mt-4">
                            <thead class="bg-[var(--surface)]">
                                <tr>
                                    <th class="border border-[var(--border)] px-4 py-2 text-left">Technology</th>
                                    <th class="border border-[var(--border)] px-4 py-2 text-left">Purpose</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">FastAPI 0.117+</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Async web framework with OpenAPI
                                        support</td>
                                </tr>
                                <tr class="bg-[var(--surface)]">
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">Python 3.13</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Runtime with latest performance
                                        features</td>
                                </tr>
                                <tr>
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">SQLAlchemy 2.x</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Async ORM for PostgreSQL</td>
                                </tr>
                                <tr class="bg-[var(--surface)]">
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">Alembic</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Database migrations</td>
                                </tr>
                                <tr>
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">Pydantic</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Data validation & serialization
                                    </td>
                                </tr>
                                <tr class="bg-[var(--surface)]">
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">HTTPX</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Async HTTP client</td>
                                </tr>
                                <tr>
                                    <td class="border border-[var(--border)] px-4 py-2 font-mono">Poetry</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Dependency management</td>
                                </tr>
                            </tbody>
                        </table>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">3.3 Key Components</h3>
                        <ul class="list-disc list-inside space-y-2 ml-4 text-[var(--text-primary)]">
                            <li><strong>RAG Service:</strong> Orchestrates Wikipedia retrieval and OpenAI response
                                generation</li>
                            <li><strong>Wikipedia Client:</strong> Interfaces with MediaWiki API for content retrieval
                            </li>
                            <li><strong>Auth Service:</strong> Handles Stytch-based authentication flows</li>
                            <li><strong>Session/Query Repositories:</strong> Manage conversation history in PostgreSQL
                            </li>
                        </ul>
                    </div>
                </section>

                <!-- Cloud Infrastructure Section -->
                <section :id="infraSection.id" class="mb-8 border-b border-[var(--border)] pb-8">
                    <button @click="toggleSection(infraSection.id)"
                        class="w-full flex items-center justify-between text-left group">
                        <h2
                            class="text-2xl font-serif font-bold text-[var(--text-primary)] group-hover:text-[var(--primary)]">
                            4. Cloud Infrastructure
                        </h2>
                        <span class="text-[var(--text-secondary)] text-xl">{{ infraSection.expanded ? '−' : '+'
                        }}</span>
                    </button>

                    <div v-show="infraSection.expanded" class="mt-4 space-y-4">
                        <p class="text-[var(--text-primary)] leading-relaxed">
                            The entire infrastructure is defined as code using <strong>Terraform</strong> and deployed
                            on
                            <strong>Amazon Web Services (AWS)</strong>. The infrastructure follows AWS Well-Architected
                            Framework principles for security, reliability, and performance.
                        </p>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">4.1 AWS Services</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                            <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4">
                                <h4 class="font-bold text-[var(--primary)] mb-2">🌐 Networking</h4>
                                <ul class="text-sm space-y-1">
                                    <li><strong>VPC:</strong> 10.0.0.0/16 CIDR block</li>
                                    <li><strong>Subnets:</strong> Public + Private across 2 AZs</li>
                                    <li><strong>NAT Gateway:</strong> Outbound internet for private subnets</li>
                                    <li><strong>Route 53:</strong> DNS management</li>
                                </ul>
                            </div>
                            <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4">
                                <h4 class="font-bold text-[var(--primary)] mb-2">⚡ Compute</h4>
                                <ul class="text-sm space-y-1">
                                    <li><strong>ECS Fargate:</strong> Serverless containers</li>
                                    <li><strong>ALB:</strong> Application Load Balancer</li>
                                    <li><strong>Auto Scaling:</strong> 1-4 tasks based on CPU</li>
                                    <li><strong>ECR:</strong> Container image registry</li>
                                </ul>
                            </div>
                            <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4">
                                <h4 class="font-bold text-[var(--primary)] mb-2">💾 Storage & Database</h4>
                                <ul class="text-sm space-y-1">
                                    <li><strong>RDS PostgreSQL:</strong> Managed database</li>
                                    <li><strong>S3:</strong> Frontend static file hosting</li>
                                    <li><strong>Secrets Manager:</strong> Secure credential storage</li>
                                </ul>
                            </div>
                            <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4">
                                <h4 class="font-bold text-[var(--primary)] mb-2">🛡️ Security & CDN</h4>
                                <ul class="text-sm space-y-1">
                                    <li><strong>CloudFront:</strong> Global CDN + SSL termination</li>
                                    <li><strong>WAF:</strong> Web Application Firewall</li>
                                    <li><strong>ACM:</strong> SSL/TLS certificates</li>
                                    <li><strong>Security Groups:</strong> Network-level access control</li>
                                </ul>
                            </div>
                        </div>


                    </div>
                </section>

                <!-- Data Flow & RAG Pipeline Section -->
                <section :id="dataFlowSection.id" class="mb-8 border-b border-[var(--border)] pb-8">
                    <button @click="toggleSection(dataFlowSection.id)"
                        class="w-full flex items-center justify-between text-left group">
                        <h2
                            class="text-2xl font-serif font-bold text-[var(--text-primary)] group-hover:text-[var(--primary)]">
                            5. Data Flow & RAG Pipeline
                        </h2>
                        <span class="text-[var(--text-secondary)] text-xl">{{ dataFlowSection.expanded ? '−' : '+'
                        }}</span>
                    </button>

                    <div v-show="dataFlowSection.expanded" class="mt-4 space-y-4">
                        <p class="text-[var(--text-primary)] leading-relaxed">
                            The heart of WikiVoice is its <strong>Retrieval-Augmented Generation (RAG)</strong>
                            pipeline, which
                            combines Wikipedia's knowledge base with OpenAI's language models to produce accurate, cited
                            responses.
                        </p>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">5.1 Query Processing
                            Flow</h3>
                        <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4 my-4">
                            <pre class="text-xs md:text-sm font-mono overflow-x-auto">
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAG PIPELINE                                      │
└─────────────────────────────────────────────────────────────────────────────┘

1. USER INPUT
   ┌──────────────┐
   │ "Tell me     │
   │ about the    │──────────────────────────────────────────┐
   │ Eiffel Tower"│                                          │
   └──────────────┘                                          ▼
                                                   ┌─────────────────┐
2. SEARCH EXTRACTION                               │   OpenAI API    │
   ┌─────────────────────────────────────────────▶│  (GPT-4o-mini)   │
   │  Prompt: "Extract key topic from query"       │                 │
   │                                               └────────┬────────┘
   │                                                        │
   │                                          "Eiffel Tower"│
   │                                                        ▼
3. WIKIPEDIA RETRIEVAL                             ┌─────────────────┐
   ┌─────────────────────────────────────────────▶│  Wikipedia API  │
   │  Search + fetch article content               │   (MediaWiki)   │
   │                                               └────────┬────────┘
   │                                                        │
   │                               Article content + sources│
   │                                                        ▼
4. CONTEXT BUILDING                                ┌─────────────────┐
   ┌─────────────────────────────────────────────▶│ Context Builder │
   │  - Wikipedia excerpts                         │  + Conversation │
   │  - Conversation history                       │     History     │
   │  - System prompt                              └────────┬────────┘
   │                                                        │
   │                                    Assembled messages  │
   │                                                        ▼
5. RESPONSE GENERATION                             ┌─────────────────┐
   ┌─────────────────────────────────────────────▶│   OpenAI API    │
   │  Generate cited response                      │    (GPT-4o)     │
   │                                               └────────┬────────┘
   │                                                        │
   │                                    AI-generated answer │
   │                                                        ▼
6. RESPONSE & STORAGE                              ┌─────────────────┐
   │  - Store query & response in PostgreSQL       │   PostgreSQL    │
   │  - Return to user                             │   (Sessions,    │
   │  - Optional: Text-to-Speech                   │    Queries)     │
   └───────────────────────────────────────────────┴─────────────────┘
              </pre>
                        </div>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">5.2 Key RAG Components
                        </h3>
                        <div class="space-y-4">
                            <div class="border-l-4 border-[var(--primary)] pl-4">
                                <h4 class="font-bold">Search Term Extraction</h4>
                                <p class="text-sm text-[var(--text-secondary)]">
                                    Uses GPT-4o-mini to extract the core topic from conversational queries.
                                    "Can you tell me about Rolex watches?" → "Rolex"
                                </p>
                            </div>
                            <div class="border-l-4 border-[var(--primary)] pl-4">
                                <h4 class="font-bold">Wikipedia Client</h4>
                                <p class="text-sm text-[var(--text-secondary)]">
                                    Queries the MediaWiki API to search for relevant articles and retrieve their
                                    content. Returns up to 3 articles with extracts (10 sentences each).
                                </p>
                            </div>
                            <div class="border-l-4 border-[var(--primary)] pl-4">
                                <h4 class="font-bold">Context Assembly</h4>
                                <p class="text-sm text-[var(--text-secondary)]">
                                    Combines Wikipedia excerpts, conversation history (last 5 messages), and a system
                                    prompt that enforces citation requirements.
                                </p>
                            </div>
                            <div class="border-l-4 border-[var(--primary)] pl-4">
                                <h4 class="font-bold">Response Generation</h4>
                                <p class="text-sm text-[var(--text-secondary)]">
                                    GPT-4o-mini generates a conversational response, strictly limited to information
                                    found in the provided Wikipedia context.
                                </p>
                            </div>
                        </div>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">5.3 Empty Context
                            Handling
                        </h3>
                        <p class="text-[var(--text-primary)] leading-relaxed mb-4">
                            Wikipedia may return empty results in several cases. When this happens, the system instructs
                            the LLM to decline answering rather than hallucinating.
                        </p>
                        <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4">
                            <h4 class="font-bold text-[var(--primary)] mb-3">When Wikipedia Returns Empty:</h4>
                            <table class="w-full text-sm">
                                <thead>
                                    <tr class="border-b border-[var(--border)]">
                                        <th class="text-left py-2 pr-4">Condition</th>
                                        <th class="text-left py-2">Why It Happens</th>
                                    </tr>
                                </thead>
                                <tbody class="text-[var(--text-secondary)]">
                                    <tr class="border-b border-[var(--border)]">
                                        <td class="py-2 pr-4 font-medium">No search results</td>
                                        <td class="py-2">Query doesn't match any Wikipedia article titles or content
                                        </td>
                                    </tr>
                                    <tr class="border-b border-[var(--border)]">
                                        <td class="py-2 pr-4 font-medium">Articles too short (&lt;500 words)</td>
                                        <td class="py-2">Stub articles are filtered out to ensure quality context</td>
                                    </tr>
                                    <tr class="border-b border-[var(--border)]">
                                        <td class="py-2 pr-4 font-medium">Extract fetch fails</td>
                                        <td class="py-2">Article exists but content couldn't be retrieved (API error)
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="py-2 pr-4 font-medium">API timeout/error</td>
                                        <td class="py-2">Wikipedia API is unreachable or returns an error</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-r mt-4">
                            <p class="text-sm text-[var(--text-primary)]">
                                <strong>Fallback Behavior:</strong> When context is empty, the system prompt instructs
                                the LLM:
                                <em>"I couldn't find relevant Wikipedia articles for your question. Please try
                                    rephrasing or ask about a different topic."</em>
                                This is a prompt-based fallback, not hard-coded logic.
                            </p>
                        </div>
                    </div>
                </section>

                <!-- Security Architecture Section -->
                <section :id="securitySection.id" class="mb-8 border-b border-[var(--border)] pb-8">
                    <button @click="toggleSection(securitySection.id)"
                        class="w-full flex items-center justify-between text-left group">
                        <h2
                            class="text-2xl font-serif font-bold text-[var(--text-primary)] group-hover:text-[var(--primary)]">
                            6. Security Architecture
                        </h2>
                        <span class="text-[var(--text-secondary)] text-xl">{{ securitySection.expanded ? '−' : '+'
                        }}</span>
                    </button>

                    <div v-show="securitySection.expanded" class="mt-4 space-y-4">
                        <p class="text-[var(--text-primary)] leading-relaxed">
                            Security is implemented at multiple layers following defense-in-depth principles.
                        </p>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">6.1 Authentication Flow
                        </h3>
                        <p class="text-[var(--text-primary)] leading-relaxed mb-4">
                            WikiVoice uses a <strong>unified auth flow</strong> that first checks if a user exists,
                            then routes to either login or registration. This provides a smooth single-form experience.
                        </p>

                        <h4 class="font-bold text-[var(--primary)] mt-4 mb-2">Step 1: Check User Exists</h4>
                        <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4 my-4">
                            <pre class="text-xs md:text-sm font-mono overflow-x-auto">
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │      │   Backend   │      │ PostgreSQL  │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │  POST /auth/       │                    │
       │  check-user        │                    │
       │  {email}           │                    │
       │───────────────────▶│                   │
       │                    │  SELECT * FROM     │
       │                    │  users WHERE email │
       │                    │───────────────────▶│
       │                    │                    │
       │                    │  User row or NULL  │
       │                    │◀───────────────────│
       │  {exists: bool}    │                    │
       │◀───────────────────│                    │
       │                    │                    │
       ▼                    │                    │
  ┌─────────┐               │                    │
  │ exists? │               │                    │
  └────┬────┘               │                    │
   yes │ no                 │                    │
       ▼                    │                    │
  Show password             │                    │
  form (login               │                    │
  OR register)              │                    │
              </pre>
                        </div>

                        <h4 class="font-bold text-[var(--primary)] mt-4 mb-2">Step 2a: Login (User Exists)</h4>
                        <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4 my-4">
                            <pre class="text-xs md:text-sm font-mono overflow-x-auto">
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │      │   Backend   │      │   Stytch    │      │ PostgreSQL  │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │                    │
       │  POST /auth/login  │                    │                    │
       │  {email, password} │                    │                    │
       │───────────────────▶│                   │                    │
       │                    │  passwords.       │                    │
       │                    │  authenticate()   │                    │
       │                    │───────────────────▶│                   │
       │                    │                    │                    │
       │                    │  {user_id,         │                    │
       │                    │   session_token}   │                    │
       │                    │◀───────────────────│                    │
       │                    │                    │                    │
       │                    │  Get local user by │                    │
       │                    │  stytch_user_id    │                    │
       │                    │────────────────────┼───────────────────▶│
       │                    │                    │                    │
       │                    │  User record       │                    │
       │                    │◀───────────────────┼────────────────────│
       │                    │                    │                    │
       │  {user_id, email}  │                    │                    │
       │  + Set-Cookie      │                    │                    │
       │◀───────────────────│                    │                    │
              </pre>
                        </div>

                        <h4 class="font-bold text-[var(--primary)] mt-4 mb-2">Step 2b: Register (New User)</h4>
                        <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4 my-4">
                            <pre class="text-xs md:text-sm font-mono overflow-x-auto">
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │      │   Backend   │      │   Stytch    │      │ PostgreSQL  │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │                    │
       │  POST /auth/       │                    │                    │
       │  register          │                    │                    │
       │  {email, password} │                    │                    │
       │───────────────────▶│                   │                    │
       │                    │  passwords.        │                    │
       │                    │  create()          │                    │
       │                    │───────────────────▶│                   │
       │                    │                    │                    │
       │                    │  {stytch_user_id,  │                    │
       │                    │   session_token}   │                    │
       │                    │◀───────────────────│                    │
       │                    │                    │                    │
       │                    │  INSERT INTO users │                    │
       │                    │  (stytch_user_id,  │                    │
       │                    │   email)           │                    │
       │                    │────────────────────┼───────────────────▶│
       │                    │                    │                    │
       │                    │  New user record   │                    │
       │                    │◀───────────────────┼────────────────────│
       │                    │                    │                    │
       │  {user_id, email}  │                    │                    │
       │  + Set-Cookie      │                    │                    │
       │◀───────────────────│                    │                    │
              </pre>
                        </div>

                        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r mt-4">
                            <p class="text-sm text-[var(--text-primary)]">
                                <strong>Why Check First?</strong> This pattern enables a unified email entry form that
                                adapts based on whether the user is new or returning. The frontend shows the
                                appropriate
                                password fields (single for login, with confirmation for register) based on the
                                response.
                            </p>
                        </div>

                        <h4 class="font-bold text-[var(--primary)] mt-6 mb-2">Password Requirements</h4>
                        <div class="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
                            <div class="bg-[var(--surface)] border border-[var(--border)] rounded p-3 text-center">
                                <span class="text-lg">📏</span>
                                <p class="font-medium mt-1">8-32 chars</p>
                            </div>
                            <div class="bg-[var(--surface)] border border-[var(--border)] rounded p-3 text-center">
                                <span class="text-lg">🔡</span>
                                <p class="font-medium mt-1">Lowercase</p>
                            </div>
                            <div class="bg-[var(--surface)] border border-[var(--border)] rounded p-3 text-center">
                                <span class="text-lg">🔠</span>
                                <p class="font-medium mt-1">Uppercase</p>
                            </div>
                            <div class="bg-[var(--surface)] border border-[var(--border)] rounded p-3 text-center">
                                <span class="text-lg">🔢</span>
                                <p class="font-medium mt-1">Number</p>
                            </div>
                            <div class="bg-[var(--surface)] border border-[var(--border)] rounded p-3 text-center">
                                <span class="text-lg">🔣</span>
                                <p class="font-medium mt-1">Symbol</p>
                            </div>
                        </div>
                        <p class="text-xs text-[var(--text-secondary)] mt-2 italic">
                            Password policies are configured in the Stytch Dashboard.
                        </p>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">6.2 Security Layers
                        </h3>
                        <table class="w-full border-collapse border border-[var(--border)] text-sm mt-4">
                            <thead class="bg-[var(--surface)]">
                                <tr>
                                    <th class="border border-[var(--border)] px-4 py-2 text-left">Layer</th>
                                    <th class="border border-[var(--border)] px-4 py-2 text-left">Protection</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="border border-[var(--border)] px-4 py-2">Edge (CloudFront + WAF)</td>
                                    <td class="border border-[var(--border)] px-4 py-2">DDoS protection, SQL injection,
                                        XSS filtering</td>
                                </tr>
                                <tr class="bg-[var(--surface)]">
                                    <td class="border border-[var(--border)] px-4 py-2">Transport</td>
                                    <td class="border border-[var(--border)] px-4 py-2">TLS 1.2+ encryption via ACM
                                        certificates</td>
                                </tr>
                                <tr>
                                    <td class="border border-[var(--border)] px-4 py-2">Network</td>
                                    <td class="border border-[var(--border)] px-4 py-2">VPC isolation, security groups,
                                        private subnets</td>
                                </tr>
                                <tr class="bg-[var(--surface)]">
                                    <td class="border border-[var(--border)] px-4 py-2">Application</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Stytch authentication, session
                                        validation</td>
                                </tr>
                                <tr>
                                    <td class="border border-[var(--border)] px-4 py-2">Data</td>
                                    <td class="border border-[var(--border)] px-4 py-2">Secrets Manager for credentials,
                                        RDS encryption</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>

                <!-- CI/CD Pipeline Section -->
                <section :id="cicdSection.id" class="mb-8 pb-8">
                    <button @click="toggleSection(cicdSection.id)"
                        class="w-full flex items-center justify-between text-left group">
                        <h2
                            class="text-2xl font-serif font-bold text-[var(--text-primary)] group-hover:text-[var(--primary)]">
                            7. CI/CD Pipeline
                        </h2>
                        <span class="text-[var(--text-secondary)] text-xl">{{ cicdSection.expanded ? '−' : '+' }}</span>
                    </button>

                    <div v-show="cicdSection.expanded" class="mt-4 space-y-4">
                        <p class="text-[var(--text-primary)] leading-relaxed">
                            The project uses <strong>GitHub Actions</strong> for continuous integration and deployment,
                            with separate workflows for infrastructure and application code.
                        </p>

                        <h3 class="text-xl font-serif font-bold text-[var(--text-primary)] mt-6">7.1 Pipeline Overview
                        </h3>
                        <div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4 my-4">
                            <pre class="text-xs md:text-sm font-mono overflow-x-auto">
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GITHUB ACTIONS WORKFLOWS                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│   Push/PR    │────▶│    Tests     │────▶│    Build     │────▶│   Deploy    │
└──────────────┘     └──────────────┘     └──────────────┘     └─────────────┘

FRONTEND PIPELINE:
  ├── npm install & lint
  ├── TypeScript type check
  ├── Build production bundle
  └── Deploy to S3 + CloudFront invalidation

BACKEND PIPELINE:
  ├── Poetry install
  ├── Ruff linting
  ├── Pytest test suite
  ├── Build Docker image
  ├── Push to ECR
  └── Update ECS service

INFRASTRUCTURE PIPELINE:
  ├── terraform fmt -check
  ├── terraform validate
  ├── terraform plan (on PR)
  └── terraform apply (on merge to main)
              </pre>
                        </div>

                        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-r">
                            <p class="text-sm text-[var(--text-primary)]">
                                <strong>⚠️ Note:</strong> The current CI/CD pipeline has some limitations.
                                See the <router-link to="/roadmap" class="text-[var(--primary)] hover:underline">Future
                                    Roadmap</router-link>
                                for planned improvements.
                            </p>
                        </div>
                    </div>
                </section>


            </main>
        </div>
    </div>
</template>
