import { config } from './config'

/**
 * Generate a random state parameter for OAuth security
 */
export function generateOAuthState(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
}

/**
 * Generate Google OAuth authorization URL
 */
export function generateGoogleOAuthUrl(state?: string): string {
  const oauthConfig = config.oauth.google
  
  if (!oauthConfig.clientId) {
    throw new Error('Google OAuth client ID is not configured')
  }

  const params = new URLSearchParams({
    client_id: oauthConfig.clientId,
    redirect_uri: oauthConfig.redirectUri,
    scope: oauthConfig.scope,
    response_type: oauthConfig.responseType,
    state: state || generateOAuthState(),
  })

  return `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`
}

/**
 * Parse OAuth callback parameters from URL
 */
export function parseOAuthCallback(url: string): { code: string; state?: string } {
  const urlObj = new URL(url)
  const code = urlObj.searchParams.get('code')
  const state = urlObj.searchParams.get('state')
  
  if (!code) {
    throw new Error('No authorization code found in OAuth callback')
  }
  
  return { code, state: state || undefined }
}

/**
 * Store OAuth state in session storage for verification
 */
export function storeOAuthState(state: string): void {
  sessionStorage.setItem('oauth_state', state)
}

/**
 * Retrieve and clear stored OAuth state
 */
export function getAndClearOAuthState(): string | null {
  const state = sessionStorage.getItem('oauth_state')
  if (state) {
    sessionStorage.removeItem('oauth_state')
    return state
  }
  return null
}

/**
 * Verify OAuth state parameter for security
 */
export function verifyOAuthState(receivedState: string): boolean {
  const storedState = getAndClearOAuthState()
  return storedState === receivedState
}
