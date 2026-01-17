# RideWise Insights - AI Coding Guidelines

## Architecture Overview
- **Frontend**: React + TypeScript + Vite, using shadcn/ui components (Radix UI primitives) with Tailwind CSS
- **Backend**: Python Flask API serving ML models for bike demand prediction
- **Data Flow**: Frontend calls backend at `http://127.0.0.1:5000` using TanStack Query; models loaded from `saved_models/`
- **Authentication**: Frontend uses AuthContext (no backend auth); routes protected with `ProtectedRoute`

## Key Patterns & Conventions
- **API Calls**: Use `src/lib/api.ts` functions with TanStack Query hooks (e.g., `useQuery`, `useMutation`)
- **Components**: Place in `src/components/`; UI primitives in `src/components/ui/` (shadcn/ui)
- **Pages**: Route-based in `src/pages/` with `AppLayout` wrapper
- **Styling**: Tailwind classes; use `class-variance-authority` for component variants
- **State Management**: React hooks + context; TanStack Query for server state
- **Error Handling**: Try-catch in API functions; display with `toast` from `use-toast.ts`

## Development Workflow
- **Start Both Servers**: Run `start-all.bat` (Windows) or `./start-all.sh` (Linux/Mac) from root
- **Backend Only**: `cd backend && python app.py` (port 5000)
- **Frontend Only**: `npm run dev` (port 5173)
- **Build**: `npm run build` for production frontend
- **Lint**: `npm run lint` (ESLint config in `eslint.config.js`)

## ML Integration
- **Models**: `best_hour_model.pkl`, `best_day_model.pkl` in `saved_models/`
- **Endpoints**: `/predict/hour`, `/predict/day` expect feature dicts matching `model.feature_names_in_`
- **Features**: Extract from request JSON; handle missing features gracefully

## File Structure Examples
- Add new page: Create in `src/pages/`, add route in `App.tsx`, wrap with `ProtectedRoute`
- Add component: `src/components/` for custom, `src/components/ui/` for shadcn/ui
- API endpoint: Add in `backend/app.py`, update `src/lib/api.ts` and types

## Common Pitfalls
- Backend port: Default 5000 (not 8000 as in some docs)
- CORS: Enabled for localhost:3000/5173; update origins list if needed
- Models: Ensure `saved_models/` exists; handle model loading errors
- Auth: Frontend checks `isAuthenticated`; backend has no auth logic</content>
<parameter name="filePath">c:\Users\shind\Downloads\bike_ride-main\.github\copilot-instructions.md