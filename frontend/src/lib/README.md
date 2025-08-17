# API Client Documentation

This directory contains the API client implementation for the HR Scouting application, based on the OpenAPI specification.

## Files

- `api-client.ts` - Main API client class with all endpoints
- `config.ts` - Configuration and environment variables

## Usage

### Basic API Client Usage

```typescript
import { apiClient } from '@/lib/api'

// Set authentication token
apiClient.setToken('your-jwt-token')

// Make API calls
const candidates = await apiClient.getCandidates(1, 10)
const jobPositions = await apiClient.getJobPositions(1, 20)
```

### Using React Hooks

```typescript
import { useCandidates, useJobPositions, useAdminUsers, useActivityLogs } from '@/hooks/use-swr-hooks'

function MyComponent() {
  const { data: candidates, isLoading, error } = useCandidates(1, 10)
  const { data: jobPositions } = useJobPositions(1, 10)
  const { data: users } = useAdminUsers(1, 100)
  const { data: activityLogs } = useActivityLogs({ page: 1, size: 10 })

  // Check loading state
  if (isLoading) {
    return <div>Loading candidates...</div>
  }

  // Handle errors
  if (error) {
    return <div>Error: {error.message}</div>
  }

  return (
    <div>
      {/* Display candidates data */}
      {candidates?.map(candidate => (
        <div key={candidate.id}>{candidate.name}</div>
      ))}
    </div>
  )
}
```

## Available Endpoints

### Authentication
- `googleCallback(code, state)` - Handle OAuth callback with authorization code
- `getCurrentUser()` - Get current authenticated user
- `logout()` - Logout user and get confirmation details

## Environment Variables

Create a `.env` file in your project root with the following variables:

### Required Variables
```bash
# Google OAuth Client ID (from Google Cloud Console)
VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id_here

# OAuth Redirect URI (must match your Google OAuth app configuration)
VITE_OAUTH_REDIRECT_URI=http://localhost:5173/login

# Backend API Base URL
VITE_API_BASE_URL=http://localhost:8000
```

### Optional Variables
```bash
# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_DEBUG_MODE=true
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Set Application Type to "Web application"
6. Add your redirect URI: `http://localhost:5173/login` (for development)
7. Copy the Client ID to your `.env` file

## OAuth Flow

The API client implements a complete OAuth 2.0 flow with frontend-generated authorization URLs:

1. **Generate OAuth URL**: Frontend generates Google OAuth URL using client ID and configuration
2. **Redirect to Google**: User is redirected to Google for authentication
3. **Google Callback**: Google redirects back to your backend with authorization code
4. **Backend Processing**: Your backend processes the code and redirects to frontend with `?callback` parameter
5. **Frontend Processing**: Frontend detects the callback parameter and calls `googleCallback()`
6. **Complete Authentication**: Frontend posts the code and state to backend and receives user token

### Frontend OAuth Configuration

Set these environment variables in your `.env` file:

```bash
VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id
VITE_OAUTH_REDIRECT_URI=http://localhost:5173/login
VITE_API_BASE_URL=http://localhost:8000
```

### Example OAuth Flow

```typescript
// 1. Start OAuth flow (frontend generates URL)
import { generateGoogleOAuthUrl, storeOAuthState } from '@/lib/oauth-utils'

const state = generateOAuthState()
storeOAuthState(state)
const authUrl = generateGoogleOAuthUrl(state)
window.location.href = authUrl

// 2. After Google redirects back to your backend, backend redirects to:
// https://yourfrontend.com/login?callback=code=ABC123&state=xyz

// 3. Frontend automatically processes the callback
// It extracts the code and state, then posts to your backend

// 4. User is authenticated and redirected to dashboard
```

### Candidates
- `getCandidates(page, size)` - Get paginated candidates
- `createCandidate(data)` - Create new candidate
- `getCandidate(id)` - Get candidate by ID
- `updateCandidate(id, data)` - Update candidate
- `deleteCandidate(id)` - Delete candidate
- `changeCandidateStatus(id, status)` - Change candidate status
- `findCandidatesBySkills(skills, page, size)` - Search by skills
- `findCandidatesBySeniority(level, page, size)` - Search by seniority

### Job Positions
- `getJobPositions(page, size)` - Get paginated job positions
- `createJobPosition(data)` - Create new job position
- `getJobPosition(id)` - Get job position by ID
- `updateJobPosition(id, data)` - Update job position
- `deleteJobPosition(id)` - Delete job position
- `changeJobPositionStatus(id, status)` - Change job position status
- `searchJobPositions(query, page, size)` - Search by text
- `getJobPositionsByStatus(status, page, size)` - Filter by status
- `getJobPositionsByEmploymentType(type, page, size)` - Filter by employment type
- `getJobPositionsBySeniorityLevel(level, page, size)` - Filter by seniority
- `getJobPositionsByLocation(city, country, page, size)` - Filter by location
- `countJobPositions(query)` - Count job positions

### Admin
- `getUsers(page, size)` - Get paginated users
- `createUser(data)` - Create new user
- `changeUserActiveStatus(id, isActive)` - Change user active status

### Health
- `healthCheck()` - Check API health

## Data Types

All API responses are fully typed using TypeScript interfaces based on the OpenAPI specification:

- `CandidateDTO` - Candidate data structure
- `JobPositionDTO` - Job position data structure
- `UserDTO` - User data structure
- `CreateCandidateDTO` - Candidate creation payload
- `UpdateCandidateDTO` - Candidate update payload
- `CreateJobPositionDTO` - Job position creation payload
- `UpdateJobPositionDTO` - Job position update payload
- `GoogleLoginResponse` - Google OAuth login URL response
- `LogoutResponse` - User logout confirmation response

## Enums

The API client includes typed enums for various status values:

- `CandidateStatus` - pending, processing, completed, failed
- `JobStatus` - pending, processing, completed, failed, open, closed, draft, archived
- `EmploymentType` - full-time, part-time, contract, internship, freelance
- `SeniorityLevel` - Junior, Mid, Senior, Lead, Principal
- `WorkArrangement`