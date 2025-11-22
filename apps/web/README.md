# WhatsApp Sales Bot - Frontend

Next.js frontend application for the WhatsApp Sales Bot SaaS platform.

## Tech Stack

- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: Axios (React Query ready)
- **Icons**: Lucide React
- **Date Formatting**: date-fns

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local and set your API URL
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
# Create production build
npm run build

# Start production server
npm start
```

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home (redirects to /login)
│   ├── login/
│   │   └── page.tsx       # Login page
│   └── dashboard/
│       ├── layout.tsx     # Dashboard layout with sidebar
│       ├── page.tsx       # Dashboard home (redirects to /chat)
│       └── chat/
│           └── page.tsx   # Main chat interface
├── components/
│   └── ui/
│       └── button.tsx     # Reusable button component
├── lib/
│   ├── api.ts            # Axios API client
│   └── auth.ts           # Auth helper functions
└── stores/
    └── auth-store.ts     # Zustand auth state
```

## Features

### Current

- ✅ Login page with authentication
- ✅ Dashboard layout with sidebar navigation
- ✅ Conversation list view
- ✅ Chat interface with message display
- ✅ Handoff controls (Take Control / Return to Bot)
- ✅ Mock data for development

### TODO

- [ ] Connect to real backend API
- [ ] Add React Query for data fetching
- [ ] Implement real-time updates (WebSocket)
- [ ] Add conversation search/filter
- [ ] Add user profile management
- [ ] Add notification system
- [ ] Improve error handling
- [ ] Add loading states
- [ ] Add tests

## API Integration

The app expects the following API endpoints (see `src/lib/api.ts`):

- `POST /auth/login` - User authentication
- `GET /conversations` - Get all conversations
- `GET /conversations/:phone/messages` - Get messages for a conversation
- `POST /conversations/:phone/take-control` - Take manual control
- `POST /conversations/:phone/return-to-bot` - Return to bot
- `POST /conversations/:phone/send` - Send manual message

## Environment Variables

Create a `.env.local` file with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Notes

- The app uses localStorage for token storage
- All API calls include the JWT token in the Authorization header
- Mock data is used for development until backend is connected
- TODO comments mark areas that need backend integration
