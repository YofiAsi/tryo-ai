# API Client Documentation

This directory contains the API client for the HR Scouting frontend.

## Usage

```typescript
import { apiClient } from '@/lib/api'

const candidates = await apiClient.candidates.getCandidates(1, 10)
const jobPositions = await apiClient.jobPositions.getJobPositions(1, 20)
```

### React hooks

```typescript
import { useCandidates, useJobPositions } from '@/hooks/use-swr-hooks'

function MyComponent() {
  const { data: candidates, isLoading, error } = useCandidates(1, 10)
  const { data: jobPositions } = useJobPositions(1, 10)
  // ...
}
```

## Environment

```bash
VITE_API_BASE_URL=http://localhost:8000
```

Optional: `VITE_ENABLE_ANALYTICS`, `VITE_DEBUG_MODE`.

## Clients

- `candidates` — candidate CRUD and search
- `jobPositions` — job position CRUD and search
- `aiAgents` — job position chat and analyzer
- `llm` — model catalog

Backend admin endpoints (`/api/v1/admin/*`) are not used by this frontend.
