# Frontend Setup Tasks

## Initial Setup
- [x] Initialize Next.js project in apps/web/
- [x] Install dependencies (@tanstack/react-query, axios, zustand, lucide-react, date-fns)

## Core Structure
- [x] Create lib/api.ts with API client
- [x] Create lib/auth.ts with auth helpers
- [x] Create stores/auth-store.ts with Zustand store
- [x] Create components/ui/button.tsx

## Pages
- [x] Update root page.tsx to redirect to /login
- [x] Create login page with functional form
- [x] Create dashboard layout with sidebar and header
- [x] Create dashboard/page.tsx redirect
- [x] Create dashboard/chat page with conversation list and chat panel

## Next Steps
- [ ] Test the application locally
- [x] Connect to backend API when ready
- [ ] Add React Query for data fetching
- [ ] Add real-time updates with WebSocket
- [ ] Improve error handling
- [ ] Add loading states
