"use client"

import { useState, useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { useNavigate, useSearchParams } from "react-router-dom"
import { Chrome, Loader2, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuth } from "@/contexts/auth-context"
import { apiClient } from "@/lib/api"
import { toast } from "@/components/ui/use-toast"
import { generateGoogleOAuthUrl, storeOAuthState, generateOAuthState } from "@/lib/oauth-utils"

export function LoginPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { login: authLogin, user, isAuthenticated } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [isProcessingCallback, setIsProcessingCallback] = useState(false)
  const hasProcessedCallback = useRef(false)

  // Check for OAuth callback
  useEffect(() => {
    // Check for Google OAuth callback parameters directly in URL
    const code = searchParams.get('code')
    const state = searchParams.get('state')
    
    if (code && !isAuthenticated && !hasProcessedCallback.current) {
      hasProcessedCallback.current = true
      handleOAuthCallback(code, state || undefined)
    }
  }, [searchParams, isAuthenticated])

  // Redirect if already authenticated
  if (isAuthenticated) {
    navigate("/")
    return null
  }

  const handleOAuthCallback = async (code: string, state?: string) => {
    try {
      setIsProcessingCallback(true)
      
      // Verify state parameter for security
      console.log(state)
      
      // Process the OAuth callback
      const response = await apiClient.auth.googleCallback(code, state)
      
      // Login with the token (this will fetch user data and update auth state)
      await authLogin(response.token.access_token)
      
      // Redirect to dashboard
      navigate("/")
      
      toast({
        title: "Login Successful",
        description: `Welcome back, ${response.user.name}!`,
      })
    } catch (error) {
      console.error('OAuth callback error:', error)
      toast({
        title: "Login Error",
        description: "Failed to complete authentication. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsProcessingCallback(false)
    }
  }

  const handleGoogleLogin = async () => {
    try {
      setIsLoading(true)
      
      // Generate OAuth state and store it
      const state = generateOAuthState()
      storeOAuthState(state)
      
      // Generate Google OAuth URL with the state
      const authUrl = generateGoogleOAuthUrl(state)
      
      // Redirect to Google OAuth
      window.location.href = authUrl
    } catch (error) {
      console.error('Google login error:', error)
      toast({
        title: "Login Error",
        description: "Failed to initiate Google login. Please try again.",
        variant: "destructive",
      })
      setIsLoading(false)
    }
  }

  // Show loading state while processing OAuth callback
  if (isProcessingCallback) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md text-center"
        >
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardContent className="p-8">
              <div className="flex items-center justify-center mb-4">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Completing Authentication
              </h3>
              <p className="text-gray-600">
                Please wait while we complete your Google sign-in...
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="text-center pb-6">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg"
            >
              <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </motion.div>
            <CardTitle className="text-2xl font-bold text-gray-900">
              Welcome to HR Scouting
            </CardTitle>
            <CardDescription className="text-gray-600">
              Sign in to manage your job positions and candidate matches
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {!isAuthenticated ? (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="space-y-4"
              >
                <Button
                  onClick={handleGoogleLogin}
                  disabled={isLoading}
                  className="w-full h-12 bg-white border-2 border-gray-200 hover:bg-gray-50 text-gray-700 font-medium relative overflow-hidden group"
                >
                  {isLoading ? (
                    <div className="flex items-center gap-3">
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Signing in...</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-3">
                      <Chrome className="h-5 w-5 text-blue-600" />
                      <span>Continue with Google</span>
                    </div>
                  )}
                </Button>
                
                <div className="text-center">
                  <p className="text-xs text-gray-500">
                    By signing in, you agree to our Terms of Service and Privacy Policy
                  </p>
                </div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className="text-center space-y-4"
              >
                                 <div className="flex items-center justify-center">
                   <div className="relative">
                     <img
                       src={user?.avatar}
                       alt={user?.name}
                       className="h-16 w-16 rounded-full border-4 border-white shadow-lg"
                     />
                     <div className="absolute -bottom-1 -right-1">
                       <CheckCircle className="h-6 w-6 text-green-500 bg-white rounded-full" />
                     </div>
                   </div>
                 </div>
                 <div>
                   <h3 className="font-semibold text-gray-900">{user?.name}</h3>
                   <p className="text-sm text-gray-600">{user?.email}</p>
                 </div>
                <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Redirecting to dashboard...</span>
                </div>
              </motion.div>
            )}
          </CardContent>
        </Card>
        
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6 text-center"
        >
          <p className="text-xs text-gray-500">
            Powered by FastAPI • MongoDB
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
} 