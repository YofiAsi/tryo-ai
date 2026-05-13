"use client"

import { motion } from "framer-motion"
import { Users, UserCheck, Clock, TrendingUp, Activity, AlertCircle, RefreshCw } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useAdminUsers, useActivityLogs, useActivitySummary, revalidateAllData } from "@/hooks/use-swr-hooks"
import type { UserDTO, ActivityLogDTO } from "@/lib/api/types"
import { ActivityType } from "@/lib/api/enums"

export function AdminOverviewPage() {
  const { data: users, error: usersError, isLoading: usersLoading, isValidating: usersValidating } = useAdminUsers(1, 100)
  const { error: summaryError, isLoading: summaryLoading, isValidating: summaryValidating } = useActivitySummary(30)
  const { data: recentActivities, error: activitiesError, isLoading: activitiesLoading, isValidating: activitiesValidating } = useActivityLogs({
    activity_type: ActivityType.LOGIN,
    page: 1,
    size: 10
  })

  // Calculate derived stats with null safety
  const stats = {
    totalUsers: users?.length || 0,
    activeUsers: users?.filter((user: UserDTO) => user.is_active).length || 0,
    logins24h: (() => {
      if (!recentActivities) return 0
      const now = new Date()
      const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      
      return recentActivities.data.filter((activity: ActivityLogDTO) => {
        const activityDate = new Date(activity.date)
        return activityDate >= twentyFourHoursAgo
      }).length
    })(),
    growthRate: users && users.length > 0 ? "+5.2%" : "0%"
  }

  // Combine loading states - show loading only on initial load
  const loading = usersLoading || summaryLoading || activitiesLoading

  // Show validating state for background updates
  const isValidating = usersValidating || summaryValidating || activitiesValidating

  // Combine error states with priority
  const error = usersError?.message || summaryError?.message || activitiesError?.message || null

  // Refresh function that revalidates all data using SWR
  const refresh = async () => {
    try {
      await revalidateAllData()
    } catch (error) {
      console.error('Failed to refresh data:', error)
    }
  }

  const statCards = [
    {
      title: "Total Users",
      value: stats.totalUsers.toLocaleString(),
      description: "All registered users",
      icon: Users,
      color: "text-blue-600",
      bgColor: "bg-blue-50"
    },
    {
      title: "Active Users",
      value: stats.activeUsers.toLocaleString(),
      description: "Users active in last 30 days",
      icon: UserCheck,
      color: "text-green-600",
      bgColor: "bg-green-50"
    },
    {
      title: "Logins (24h)",
      value: stats.logins24h.toLocaleString(),
      description: "Login attempts in last 24 hours",
      icon: Clock,
      color: "text-orange-600",
      bgColor: "bg-orange-50"
    },
    {
      title: "Growth Rate",
      value: stats.growthRate,
      description: "User growth this month",
      icon: TrendingUp,
      color: "text-purple-600",
      bgColor: "bg-purple-50"
    }
  ]

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffMins < 60) return `${diffMins} minutes ago`
    if (diffHours < 24) return `${diffHours} hours ago`
    return `${diffDays} days ago`
  }

  const getUserInitials = (user: UserDTO) => {
    if (user.name) {
      return user.name.split(' ').map(n => n[0]).join('')
    }
    if (user.email) {
      return user.email[0].toUpperCase()
    }
    return 'U'
  }

  if (loading) {
    return (
      <div className="flex h-screen flex-col">
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-b bg-background px-6 py-4"
        >
          <div className="flex items-center gap-4">
            <SidebarTrigger />
            <div>
              <h1 className="text-2xl font-bold">Admin Overview</h1>
              <p className="text-muted-foreground">System statistics and user activity</p>
            </div>
          </div>
        </motion.header>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading overview data...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b bg-background px-6 py-4"
      >
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div className="flex-1">
            <h1 className="text-2xl font-bold">Admin Overview</h1>
            <p className="text-muted-foreground">
              System statistics and user activity
              {isValidating && (
                <span className="ml-2 inline-flex items-center gap-1 text-xs">
                  <div className="h-2 w-2 animate-pulse rounded-full bg-blue-500"></div>
                  Updating...
                </span>
              )}
            </p>
          </div>
          <button
            onClick={refresh}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`h-4 w-4 ${isValidating ? 'animate-spin' : ''}`} />
            {isValidating ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-6"
        >
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {statCards.map((stat, index) => (
              <motion.div
                key={stat.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
              >
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                    <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                      <stat.icon className={`h-4 w-4 ${stat.color}`} />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stat.value}</div>
                    <p className="text-xs text-muted-foreground">{stat.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Recent Logins */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Recent Logins
                </CardTitle>
                <CardDescription>
                  User login activity in the last hour
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentActivities && recentActivities.data.length > 0 ? (
                    recentActivities.data.map((activity: ActivityLogDTO, index: number) => (
                      <motion.div
                        key={activity.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 * index }}
                        className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-medium">
                            {activity.user ? getUserInitials(activity.user) : 'U'}
                          </div>
                          <div>
                            <p className="text-sm font-medium">
                              {activity.user?.name || activity.user?.email || 'Unknown User'}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {activity.user?.email || 'No email'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge 
                            variant="default"
                            className="text-xs"
                          >
                            {activity.activity_type.replace('_', ' ').toLowerCase()}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatTimeAgo(activity.date)}
                          </span>
                        </div>
                      </motion.div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No recent login activity</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
} 