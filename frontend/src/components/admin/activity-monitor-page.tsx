"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { 
  Activity, 
  Search, 
  Filter, 
  Calendar,
  User,
  LogIn,
  LogOut,
  Edit,
  Trash2,
  Plus,
  Eye,
  RefreshCw,
  Loader2,
  ChevronLeft,
  ChevronRight,
  MoreHorizontal
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useActivityLogs, useActivitySummary, revalidateAllData } from "@/hooks/use-swr-hooks"
import { ActivityType } from "@/lib/api/enums"


const actionIcons = {
  [ActivityType.LOGIN]: LogIn,
  [ActivityType.LOGOUT]: LogOut,
  [ActivityType.NEW_JOB_POSITION]: Plus,
  [ActivityType.UPDATE_JOB_POSITION]: Edit,
  [ActivityType.DELETE_JOB_POSITION]: Trash2,
  [ActivityType.NEW_CANDIDATE]: Eye,
  [ActivityType.USER_CREATED]: User
}

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100]

export function ActivityMonitorPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [actionFilter, setActionFilter] = useState<ActivityType | "all">("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [dateFilter, setDateFilter] = useState("all")
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)

  // Use SWR hooks for data fetching
  const { 
    data: activityLogsResponse, 
    error: logsError, 
    isLoading: logsLoading,
    isValidating: logsValidating 
  } = useActivityLogs({
    activity_type: actionFilter === "all" ? undefined : actionFilter,
    page: currentPage,
    size: pageSize
  })

  const { 
    error: summaryError, 
    isLoading: summaryLoading 
  } = useActivitySummary(30)

  const handleRetry = async () => {
    try {
      await revalidateAllData()
    } catch (error) {
      console.error('Failed to retry:', error)
    }
  }

  // Extract data and total count from response
  const activityLogs = activityLogsResponse?.data || []
  const totalCount = activityLogsResponse?.totalCount || 0

  // Filter activity logs based on search term and filters
  const filteredLogs = activityLogs.filter((log) => {
    const matchesSearch =
      log.user?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.user?.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.activity_type?.toLowerCase().includes(searchTerm.toLowerCase())
    // Note: ActivityLogDTO doesn't have status field, so we'll skip status filtering for now
    return matchesSearch
  })

  // Calculate pagination info using the actual total count from API
  const totalItems = totalCount
  const totalPages = Math.ceil(totalItems / pageSize)
  const startItem = (currentPage - 1) * pageSize + 1
  const endItem = Math.min(currentPage * pageSize, totalItems)

  // Show pagination if we have more items than page size or if we're not on the first page
  const shouldShowPagination = totalItems > pageSize || currentPage > 1

  // Handle page size change
  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize)
    setCurrentPage(1) // Reset to first page when changing page size
  }

  // Handle page navigation
  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  // Generate page numbers for pagination
  const getPageNumbers = () => {
    const pages = []
    const maxVisiblePages = 5
    
    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) {
          pages.push(i)
        }
        pages.push('ellipsis')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 2) {
        pages.push(1)
        pages.push('ellipsis')
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pages.push(i)
        }
      } else {
        pages.push(1)
        pages.push('ellipsis')
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i)
        }
        pages.push('ellipsis')
        pages.push(totalPages)
      }
    }
    
    return pages
  }

  const getActionIcon = (action: string) => {
    const IconComponent = actionIcons[action as keyof typeof actionIcons] || Activity
    return <IconComponent className="h-4 w-4" />
  }



  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString()
  }

  // Handle loading state
  if (logsLoading || summaryLoading) {
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
              <h1 className="text-2xl font-bold">Activity Monitor</h1>
              <p className="text-muted-foreground">Monitor system activity and user actions</p>
            </div>
          </div>
        </motion.header>
        
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
            <p className="text-muted-foreground">Loading activity logs...</p>
          </div>
        </div>
      </div>
    )
  }

  // Handle error state
  if (logsError || summaryError) {
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
              <h1 className="text-2xl font-bold">Activity Monitor</h1>
              <p className="text-muted-foreground">Monitor system activity and user actions</p>
            </div>
          </div>
        </motion.header>
        
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center space-y-4">
            <p className="text-lg text-muted-foreground mb-4">
              {logsError?.message || summaryError?.message || 'Failed to load activity logs. Please try again.'}
            </p>
            <Button onClick={handleRetry}>Try Again</Button>
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
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <SidebarTrigger />
            <div>
              <h1 className="text-2xl font-bold">Activity Monitor</h1>
              <p className="text-muted-foreground">Monitor system activity and user actions</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button 
              onClick={handleRetry} 
              variant="outline" 
              size="sm"
              disabled={logsLoading}
              className="gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${logsValidating ? 'animate-spin' : ''}`} />
              {logsValidating ? 'Refreshing...' : 'Refresh'}
            </Button>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-6"
        >
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Activity Logs ({totalCount} total)
              </CardTitle>
              <CardDescription>
                Monitor user actions and system events
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex flex-1 items-center gap-4">
                  <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Search activities..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Select value={actionFilter} onValueChange={(value) => setActionFilter(value as ActivityType | "all")}>
                    <SelectTrigger className="w-[140px]">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Action" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Actions</SelectItem>
                      <SelectItem value={ActivityType.LOGIN}>Login</SelectItem>
                      <SelectItem value={ActivityType.LOGOUT}>Logout</SelectItem>
                      <SelectItem value={ActivityType.NEW_JOB_POSITION}>Create Position</SelectItem>
                      <SelectItem value={ActivityType.UPDATE_JOB_POSITION}>Update Position</SelectItem>
                      <SelectItem value={ActivityType.DELETE_JOB_POSITION}>Delete Position</SelectItem>
                      <SelectItem value={ActivityType.NEW_CANDIDATE}>New Candidate</SelectItem>
                      <SelectItem value={ActivityType.USER_CREATED}>Create User</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-[140px]">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="success">Success</SelectItem>
                      <SelectItem value="failed">Failed</SelectItem>
                      <SelectItem value="warning">Warning</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={dateFilter} onValueChange={setDateFilter}>
                    <SelectTrigger className="w-[140px]">
                      <Calendar className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Date" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Time</SelectItem>
                      <SelectItem value="today">Today</SelectItem>
                      <SelectItem value="week">This Week</SelectItem>
                      <SelectItem value="month">This Month</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Show:</span>
                  <Select value={pageSize.toString()} onValueChange={(value) => handlePageSizeChange(parseInt(value))}>
                    <SelectTrigger className="w-[80px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PAGE_SIZE_OPTIONS.map(size => (
                        <SelectItem key={size} value={size.toString()}>
                          {size}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Activity Table */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="rounded-md border"
          >
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Activity Type</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLogs.map((log, index) => (
                  <motion.tr
                    key={log.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="hover:bg-muted/50 transition-colors"
                  >
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-medium">
                          {log.user?.name?.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div>
                          <p className="text-sm font-medium">{log.user?.name}</p>
                          <p className="text-xs text-muted-foreground">{log.user?.email}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getActionIcon(log.activity_type)}
                        <span className="text-sm capitalize">{log.activity_type.replace('_', ' ')}</span>
                      </div>
                    </TableCell>
                    <TableCell className="max-w-xs">
                      <p className="text-sm truncate" title={log.activity_type}>
                        {log.activity_type.replace(/_/g, ' ')}
                      </p>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      <code className="text-xs bg-muted px-1 py-0.5 rounded">
                        {log.ip_address || 'N/A'}
                      </code>
                    </TableCell>
                    <TableCell>
                      <Badge variant="default">
                        Success
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      <div className="text-xs">
                        {formatTimestamp(log.date)}
                      </div>
                    </TableCell>
                  </motion.tr>
                ))}
              </TableBody>
            </Table>
          </motion.div>

          {/* Pagination */}
          {shouldShowPagination && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="flex items-center justify-between p-4 border rounded-lg bg-muted/50"
            >
              <div className="text-sm text-muted-foreground">
                Showing {startItem} to {endItem} of {totalItems} results
                <br />
                <span className="text-xs">Page {currentPage} of {totalPages} (Page size: {pageSize})</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="gap-2"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                
                <div className="flex items-center space-x-1">
                  {getPageNumbers().map((page, index) => (
                    <div key={index}>
                      {page === 'ellipsis' ? (
                        <span className="flex h-9 w-9 items-center justify-center text-muted-foreground">
                          <MoreHorizontal className="h-4 w-4" />
                        </span>
                      ) : (
                        <Button
                          variant={currentPage === page ? "outline" : "ghost"}
                          size="sm"
                          onClick={() => handlePageChange(page as number)}
                          className="h-9 w-9 p-0"
                        >
                          {page}
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="gap-2"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  )
} 