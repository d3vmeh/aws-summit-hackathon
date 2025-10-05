# Burnout Prevention Agent - Frontend

Next.js 15 frontend with TypeScript, Tailwind CSS, and shadcn/ui components.

## Features

- **Real-time Stress Dashboard** - Visualize stress levels with progress bars and risk indicators
- **AI Predictions** - Display burnout predictions from Amazon Bedrock (Claude Sonnet 4.5)
- **Intervention Recommendations** - Show personalized actions to reduce burnout risk
- **Responsive Design** - Works on desktop and mobile
- **Modern UI** - Built with shadcn/ui components and Tailwind CSS

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running on port 8001

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start the development server
npm run dev
```

The app will be available at:
- **http://localhost:3000** (or next available port like 3003)

### Build for Production

```bash
# Build the app
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page (uses StressDashboard)
│   └── globals.css         # Global styles
├── components/
│   ├── ui/                 # shadcn/ui components
│   └── stress-dashboard.tsx  # Main dashboard component
├── lib/
│   ├── api.ts              # Backend API client
│   ├── types.ts            # TypeScript interfaces
│   ├── mock-data.ts        # Demo data (UCLA student)
│   └── utils.ts            # Utility functions
└── .env.local              # Environment variables
```

## Environment Variables

Create a `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Components

### StressDashboard

Main component that:
1. Fetches mock data (events and tasks)
2. Calls backend API to analyze stress
3. Displays:
   - Overall stress score (0-100)
   - Risk level badge (Low/Medium/High/Critical)
   - Individual factors (Calendar, Tasks, Sleep)
   - AI predictions from Bedrock
   - Recommended interventions

### UI Components (shadcn/ui)

- **Card** - Container for dashboard sections
- **Progress** - Visual stress level indicators
- **Badge** - Risk level and priority tags

## How It Works

1. **Load Mock Data** - Uses UCLA student schedule from `lib/mock-data.ts`
2. **API Call** - Sends events and tasks to `POST /api/stress/analyze`
3. **Display Results** - Shows stress score, AI predictions, and interventions
4. **Auto-refresh** - Click "Refresh Analysis" to re-analyze

## Customization

### Change Mock Data

Edit `lib/mock-data.ts` to change the demo schedule:

```typescript
export const mockEvents: CalendarEvent[] = [
  {
    id: "1",
    summary: "Your Event",
    start: new Date(...).toISOString(),
    end: new Date(...).toISOString(),
  }
];
```

### Change Colors

Colors are defined in `app/globals.css` using Tailwind CSS variables.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Components**: shadcn/ui
- **Bundler**: Turbopack (faster than Webpack)
- **Icons**: Lucide React (from shadcn)

## Development Notes

- Uses **client-side rendering** ("use client" in dashboard component)
- API calls are made from the browser to backend at `localhost:8001`
- Mock data is used for demo - replace with real Google Calendar integration later
- All datetime values use ISO 8601 format (e.g., `2025-10-04T14:30:00Z`)

## Next Steps

- [ ] Add Google Calendar OAuth integration
- [ ] Add loading skeletons
- [ ] Add error boundaries
- [ ] Add unit tests with Jest
- [ ] Deploy to Vercel or AWS Amplify
