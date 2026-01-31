# WikiVoice Frontend

Vue 3 SPA frontend for WikiVoice - a voice-enabled Wikipedia query application.

## 🛠️ Tech Stack

- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite 7
- **Language**: TypeScript
- **State**: Pinia
- **Routing**: Vue Router 5
- **Styling**: Tailwind CSS
- **Auth**: Stytch SDK
- **Testing**: Vitest

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/           # API client & endpoints
│   ├── assets/        # Static assets (images, fonts)
│   ├── components/    # Reusable Vue components
│   ├── composables/   # Vue composables (shared logic)
│   ├── lib/           # Utility libraries
│   ├── router/        # Vue Router configuration
│   ├── stores/        # Pinia state stores
│   └── views/         # Page components
├── public/            # Public static files
├── index.html         # Entry HTML
└── vite.config.ts     # Vite configuration
```

## 🚀 Getting Started

### Prerequisites

- Node.js 20+
- npm 10+

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

## ⚙️ Environment Variables

Create a `.env.local` file:

```env
VITE_API_URL=http://localhost:8000
VITE_STYTCH_PUBLIC_TOKEN=your-stytch-public-token
```

## 📜 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Lint and fix code |
| `npm run type-check` | Run TypeScript checks |
| `npm test` | Run tests once |
| `npm run test:watch` | Run tests in watch mode |
| `npm run test:coverage` | Run tests with coverage |

## 🧪 Testing

```bash
# Run all tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

## 🔍 Code Quality

```bash
# ESLint
npm run lint

# Type checking
npm run type-check
```

## 🏗️ Building for Production

```bash
# Build
npm run build

# Preview build locally
npm run preview
```

Output will be in the `dist/` directory.

## 🎨 Styling

This project uses Tailwind CSS. Configuration is in `tailwind.config.js`.

```html
<!-- Example Tailwind usage -->
<button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  Button
</button>
```

## 📡 API Integration

API client is configured in `src/api/`. Axios is used for HTTP requests.

```typescript
// Example API call
import { api } from '@/api'

const response = await api.query.submit({ question: 'What is Vue.js?' })
```

## 📄 License

Private - All rights reserved.
