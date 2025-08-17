"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
import useSWR from "swr"
import { swrFetcher, swrKeys, authSWRConfig } from "@/lib/api/swr-fetcher"
import { AuthUserResponse } from "@/lib/api"
import { apiClient } from "@/lib/api"

interface User {
  id: string
  name: string
  email: string
  avatar?: string
  role: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: () => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
  setToken: (token: string) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isInitializing, setIsInitializing] = useState(true)
  const [currentToken, setCurrentToken] = useState<string | null>(null)

  // Helper function to check if an error should trigger token clearing
  const shouldClearToken = (error: any): boolean => {
    return error?.message === "No auth token available" || 
           error?.status === 401 || 
           error?.status === 403 || 
           error?.status === 404 || 
           error?.status === 500 || 
           error?.status === 502 || 
           error?.status === 503 || 
           error?.status === 504 ||
           (error?.status && error.status >= 400) ||
           error?.message?.includes('API Error')
  }

  // Helper function to clear token
  const clearToken = () => {
    console.log('Clearing auth token')
    localStorage.removeItem("auth_token")
    setCurrentToken(null)
    apiClient.setToken("")
  }

  // Update token state when localStorage changes
  useEffect(() => {
    const updateToken = () => {
      const token = localStorage.getItem("auth_token")
      console.log('Token update called:', token ? 'exists' : 'none')
      setCurrentToken(token)
      if (token) {
        apiClient.setToken(token)
        console.log('Token set in API client')
      } else {
        apiClient.setToken("")
        console.log('Token cleared from API client')
      }
      // Always set initializing to false after token check
      setIsInitializing(false)
      console.log('Initializing set to false')
    }

    // Initial token check
    console.log('Initial token check starting')
    updateToken()

    // Listen for storage changes (in case token is set from another tab/window)
    window.addEventListener('storage', updateToken)
    
    return () => {
      window.removeEventListener('storage', updateToken)
    }
  }, [])

  // Use SWR for user data with proper caching
  const { 
    data: apiUser, 
    isLoading: swrLoading,
    mutate: mutateUser 
  } = useSWR(
    () => {
      if (!currentToken) return null
      
      // Create a stable key that includes token hash to prevent unnecessary re-renders
      const tokenHash = btoa(currentToken).slice(0, 8) // Simple hash for demo
      const key = `${swrKeys.auth.currentUser}?token=${tokenHash}`
      console.log('Auth SWR key:', key, 'Token exists:', !!currentToken)
      return key
    },
    swrFetcher.auth.currentUser,
    {
      ...authSWRConfig,
      onSuccess: () => {
        console.log('Auth request successful')
      },
      onError: (error) => {
        console.log('Auth request failed:', error)
        console.log('Error details:', {
          message: error?.message,
          status: error?.status,
          statusText: error?.statusText,
          stack: error?.stack
        })
        
        // If auth fails with any non-200 status or specific error messages, clear the token
        if (shouldClearToken(error)) {
          console.log('Clearing invalid token due to error:', error?.status || error?.message)
          clearToken()
        } else {
          console.log('Error not considered auth failure, keeping token')
        }
      },
    }
  )

  // Convert API user response to local User interface
  const mapApiUserToUser = (apiUser: AuthUserResponse): User => ({
    id: apiUser.id,
    name: apiUser.name,
    email: apiUser.email,
    avatar: apiUser.picture,
    role: apiUser.role,
  })

  const user = apiUser ? mapApiUserToUser(apiUser) : null
  const isAuthenticated = !!user

  // Determine loading state: only loading if we're initializing OR if we have a token and SWR is loading
  const isLoading = isInitializing || (!!currentToken && swrLoading)
  
  console.log('Loading state calculation:', {
    isInitializing,
    hasToken: !!currentToken,
    swrLoading,
    finalLoadingState: isLoading
  })

  const refreshUser = async (): Promise<void> => {
    try {
      await mutateUser()
    } catch (error: unknown) {
      console.error("Failed to refresh user:", error)
      // Only clear token for auth-related errors
      const errorObj = error as any
      if (shouldClearToken(errorObj)) {
        console.log('Clearing invalid token in refreshUser due to error:', errorObj?.status || errorObj?.message)
        clearToken()
      }
      throw error
    }
  }

  const setToken = (token: string) => {
    console.log('Setting token:', token ? 'exists' : 'none')
    localStorage.setItem("auth_token", token)
    setCurrentToken(token)
    apiClient.setToken(token)
  }

  const login = async (): Promise<void> => {
    try {
      setIsInitializing(true)
      // Get current user from API (token should already be set from OAuth callback)
      await refreshUser()
    } catch (error) {
      console.error("Login failed:", error)
      throw error
    } finally {
      setIsInitializing(false)
    }
  }

  const logout = async (): Promise<void> => {
    try {
      // Call logout API if user is authenticated
      if (user) {
        await apiClient.auth.logout()
      }
    } catch (error) {
      console.error("Logout API call failed:", error)
      // Continue with local logout even if API call fails
    } finally {
      // Clear local data
      clearToken()
      // Clear SWR cache for user
      mutateUser(undefined, false)
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshUser,
    setToken
  }

  // Debug logging
  console.log('Auth state:', {
    isInitializing,
    swrLoading,
    hasToken: !!currentToken,
    user: !!user,
    isAuthenticated
  })

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
} 