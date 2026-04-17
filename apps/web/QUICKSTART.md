# Quick Start Guide - Frontend

## Setup Steps

1. **Navigate to the web directory**
   ```bash
   cd apps/web
   ```

2. **Install dependencies** (already done)
   ```bash
   npm install
   ```

3. **Create environment file**
   ```bash
   # Copy the example (or create manually)
   echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   - Navigate to: http://localhost:3000
   - You'll be redirected to /login
   - Use any credentials (backend not connected yet)

## What's Working

✅ Next.js project initialized with TypeScript and Tailwind CSS
✅ Login page with form
✅ Dashboard layout with sidebar
✅ Chat interface with mock data
✅ Handoff controls (UI only)
✅ All dependencies installed

## What Needs Backend

The following features have placeholder/mock data and need backend connection:

- [ ] `/auth/login` - User authentication
- [ ] `/conversations` - Get conversation list
- [ ] `/conversations/:phone/messages` - Get messages
- [ ] `/conversations/:phone/take-control` - Take manual control
- [ ] `/conversations/:phone/return-to-bot` - Return to bot
- [ ] `/conversations/:phone/send` - Send message

## File Structure Created

```
apps/web/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Redirect to /login
│   │   ├── login/
│   │   │   └── page.tsx            # Login page
│   │   └── dashboard/
│   │       ├── layout.tsx          # Dashboard with sidebar
│   │       ├── page.tsx            # Redirect to /chat
│   │       └── chat/
│   │           └── page.tsx        # Main chat interface
│   ├── components/
│   │   └── ui/
│   │       └── button.tsx          # Reusable button
│   ├── lib/
│   │   ├── api.ts                  # API client with all methods
│   │   └── auth.ts                 # Auth helpers
│   └── stores/
│       └── auth-store.ts           # Zustand auth state
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── README.md
```

## Next Steps

1. Connect to backend API endpoints
2. Add React Query for data fetching
3. Implement WebSocket for real-time updates
4. Add error handling and loading states
5. Add tests
