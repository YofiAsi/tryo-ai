// Configuration for the HR Scouting application

export const config = {
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 30000,
    retryAttempts: 3,
  },
  oauth: {
    google: {
      clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || '111073171763-1n5di4no5bkak2sbl5l2lpq40kdog7vf.apps.googleusercontent.com',
      redirectUri: import.meta.env.VITE_OAUTH_REDIRECT_URI || 'http://localhost:8000/login',
      scope: 'openid email profile',
      responseType: 'code',
    },
  },
  pagination: {
    defaultPageSize: 10,
    maxPageSize: 100,
  },
  features: {
    enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
    enableDebugMode: import.meta.env.VITE_DEBUG_MODE === 'true',
  },
} as const
