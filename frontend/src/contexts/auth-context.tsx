"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
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
  login: (token: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const TOKEN_KEY = "auth_token"

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const isAuthenticated = !!user

  // Convert API user response to local User interface
  const mapApiUserToUser = (apiUser: AuthUserResponse): User => ({
    id: apiUser.id,
    name: apiUser.name,
    email: apiUser.email,
    avatar: apiUser.picture,
    role: apiUser.role,
  })

  // Get current user from API
  const fetchCurrentUser = async (): Promise<User | null> => {
    try {
      const apiUser = await apiClient.auth.getCurrentUser()
      return mapApiUserToUser(apiUser)
    } catch (error) {
      // If we get a 401, the token is invalid
      if ((error as any)?.status === 401) {
        localStorage.removeItem(TOKEN_KEY)
        apiClient.setToken("")
        return null
      }
      throw error
    }
  }

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem(TOKEN_KEY)
        
        if (token) {
          apiClient.setToken(token)
          const currentUser = await fetchCurrentUser()
          setUser(currentUser)
        }
      } catch (error) {
        console.error("Failed to initialize authentication:", error)
        // Clear invalid token
        localStorage.removeItem(TOKEN_KEY)
        apiClient.setToken("")
      } finally {
        setIsLoading(false)
      }
    }

    initializeAuth()
  }, [])

  const login = async (token: string): Promise<void> => {
    try {
      setIsLoading(true)
      
      // Store token
      localStorage.setItem(TOKEN_KEY, token)
      apiClient.setToken(token)
      
      // Fetch user data
      const currentUser = await fetchCurrentUser()
      setUser(currentUser)
    } catch (error) {
      console.error("Login failed:", error)
      // Clear token on failure
      localStorage.removeItem(TOKEN_KEY)
      apiClient.setToken("")
      throw error
    } finally {
      setIsLoading(false)
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
      localStorage.removeItem(TOKEN_KEY)
      apiClient.setToken("")
      setUser(null)
    }
  }

  const refreshUser = async (): Promise<void> => {
    try {
      const currentUser = await fetchCurrentUser()
      setUser(currentUser)
    } catch (error) {
      console.error("Failed to refresh user:", error)
      throw error
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshUser
  }

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