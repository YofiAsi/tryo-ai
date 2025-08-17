// Authentication API Client

import { BaseApiClient } from './base-client'
import type {

  GoogleLoginResponse,
  LoginResponse,
  LogoutResponse,
  AuthUserResponse
} from './types'

export class AuthClient extends BaseApiClient {
  // Get Google OAuth2 Login URL
  async getGoogleLoginUrl(): Promise<GoogleLoginResponse> {
    return this.request<GoogleLoginResponse>('/api/v1/auth/google/login')
  }

  // Google OAuth2 Callback
  async googleCallback(code: string, state?: string): Promise<LoginResponse> {
    return this.request<LoginResponse>('/api/v1/auth/google/callback', {
      method: 'POST',
      body: JSON.stringify({ code, state }),
    })
  }

  // Handle OAuth callback from URL parameters
  async handleOAuthCallback(callbackData: string): Promise<LoginResponse> {
    const params = new URLSearchParams(callbackData)
    const code = params.get('code')
    const state = params.get('state')
    
    if (!code) {
      throw new Error('No authorization code received from OAuth provider')
    }
    
    return this.googleCallback(code, state || undefined)
  }

  // Get current authenticated user
  async getCurrentUser(): Promise<AuthUserResponse> {
    return this.request<AuthUserResponse>('/api/v1/auth/me')
  }

  // Logout user
  async logout(): Promise<LogoutResponse> {
    return this.request<LogoutResponse>('/api/v1/auth/logout', {
      method: 'POST',
    })
  }
}
