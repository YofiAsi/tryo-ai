"use client"

import { ReactNode } from "react"
import { Navigate } from "react-router-dom"
import { useAuth } from "@/contexts/auth-context"
import { Loader2 } from "lucide-react"

interface AdminRouteProps {
  children: ReactNode
}

export function AdminRoute({ children }: AdminRouteProps) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user || user.role !== "admin") {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
} 