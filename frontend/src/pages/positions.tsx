"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Search, Filter, ChevronLeft, ChevronRight, ExternalLink, Loader2, Plus, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { useNavigate } from "react-router-dom"
import { useJobPositions, useJobPositionSearch, revalidateAllData } from "@/hooks/use-swr-hooks"
import { JobStatus } from "@/lib/api"


const ITEMS_PER_PAGE = 10

export function PositionsPage() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<JobStatus | "all">("all")
  const [currentPage, setCurrentPage] = useState(1)

  // Use SWR hooks for data fetching
  const { 
    data: positions = [], 
    error: positionsError, 
    isLoading: positionsLoading,
    isValidating: positionsValidating 
  } = useJobPositions(currentPage, ITEMS_PER_PAGE)

  const { 
    data: searchResults = [], 
    error: searchError, 
    isLoading: searchLoading,
    isValidating: searchValidating 
  } = useJobPositionSearch(searchTerm, currentPage, ITEMS_PER_PAGE)

  // Determine which data to use and loading states
  const isSearching = searchTerm.length > 0
  const data = isSearching ? searchResults : positions
  const error = isSearching ? searchError : positionsError
  const isLoading = isSearching ? searchLoading : positionsLoading
  const isValidating = isSearching ? searchValidating : positionsValidating

  // Filter positions by status
  const filteredPositions = data.filter((position) => {
    if (statusFilter === "all") return true
    return position.status === statusFilter
  })

  const handleSearchChange = (value: string) => {
    setSearchTerm(value)
    setCurrentPage(1)
  }

  const handleStatusChange = (value: string) => {
    setStatusFilter(value as JobStatus | "all")
    setCurrentPage(1)
  }

  const handleRetry = async () => {
    try {
      await revalidateAllData()
    } catch (error) {
      console.error('Failed to retry:', error)
    }
  }

  const getStatusBadgeVariant = (status: JobStatus) => {
    switch (status) {
      case JobStatus.OPEN:
        return "default"
      case JobStatus.CLOSED:
        return "secondary"
      case JobStatus.DRAFT:
        return "outline"
      case JobStatus.ARCHIVED:
        return "destructive"
      case JobStatus.PENDING:
        return "outline"
      case JobStatus.PROCESSING:
        return "default"
      case JobStatus.COMPLETED:
        return "secondary"
      case JobStatus.FAILED:
        return "destructive"
      default:
        return "default"
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const totalPages = Math.ceil(data.length / ITEMS_PER_PAGE) // This will be incorrect as data is not paginated

  if (error && !isLoading) {
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
              <h1 className="text-2xl font-bold">Positions</h1>
              <p className="text-muted-foreground">Manage and track your job positions</p>
            </div>
          </div>
        </motion.header>
        
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center">
            <p className="text-lg text-muted-foreground mb-4">
              {error instanceof Error ? error.message : 'Failed to load positions. Please try again.'}
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
              <h1 className="text-2xl font-bold">Positions</h1>
              <p className="text-muted-foreground">
                Manage and track your job positions
                {isValidating && (
                  <span className="ml-2 inline-flex items-center gap-1 text-xs">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500"></span>
                    Updating...
                  </span>
                )}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button 
              onClick={handleRetry} 
              variant="outline" 
              size="sm"
              disabled={isLoading}
              className="gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${isValidating ? 'animate-spin' : ''}`} />
              {isValidating ? 'Refreshing...' : 'Refresh'}
            </Button>
            <Button onClick={() => navigate("/positions/add")} className="gap-2">
              <Plus className="h-4 w-4" />
              Add Position
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
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-1 items-center gap-4">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search positions or companies..."
                  value={searchTerm}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={handleStatusChange}>
                <SelectTrigger className="w-[180px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value={JobStatus.OPEN}>Open</SelectItem>
                  <SelectItem value={JobStatus.CLOSED}>Closed</SelectItem>
                  <SelectItem value={JobStatus.DRAFT}>Draft</SelectItem>
                  <SelectItem value={JobStatus.ARCHIVED}>Archived</SelectItem>
                  <SelectItem value={JobStatus.PENDING}>Pending</SelectItem>
                  <SelectItem value={JobStatus.PROCESSING}>Processing</SelectItem>
                  <SelectItem value={JobStatus.COMPLETED}>Completed</SelectItem>
                  <SelectItem value={JobStatus.FAILED}>Failed</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="text-sm text-muted-foreground">
              {isLoading ? "Loading..." : `${filteredPositions.length} position${filteredPositions.length !== 1 ? "s" : ""} found`}
            </div>
          </div>

          {/* Table */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="rounded-md border"
          >
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Position Title</TableHead>
                  <TableHead>Company</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Employment Type</TableHead>
                  <TableHead>Seniority</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8">
                      <div className="flex items-center justify-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Loading positions...
                      </div>
                    </TableCell>
                  </TableRow>
                ) : filteredPositions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                      No positions found
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredPositions.map((position, index) => (
                    <motion.tr
                      key={position.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 * index }}
                      className="hover:bg-muted/50 transition-colors cursor-pointer"
                      onClick={() => navigate(`/positions/${position.id}`)}
                    >
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          {position.title || "Untitled Position"}
                          <ExternalLink className="h-3 w-3 text-muted-foreground" />
                        </div>
                      </TableCell>
                      <TableCell>{position.company || "Unknown Company"}</TableCell>
                      <TableCell>
                        <Badge variant={getStatusBadgeVariant(position.status)}>
                          {position.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {position.created_at ? formatDate(position.created_at) : "Unknown"}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {position.employment_type || "Not specified"}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {position.seniority_level || "Not specified"}
                      </TableCell>
                    </motion.tr>
                  ))
                )}
              </TableBody>
            </Table>
          </motion.div>

          {/* Pagination */}
          {totalPages > 1 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="flex items-center justify-between"
            >
              <div className="text-sm text-muted-foreground">
                Showing {((currentPage - 1) * ITEMS_PER_PAGE) + 1} to {Math.min(currentPage * ITEMS_PER_PAGE, data.length)} of {data.length} results
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    let pageNum
                    if (totalPages <= 5) {
                      pageNum = i + 1
                    } else if (currentPage <= 3) {
                      pageNum = i + 1
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i
                    } else {
                      pageNum = currentPage - 2 + i
                    }
                    
                    return (
                      <Button
                        key={pageNum}
                        variant={currentPage === pageNum ? "default" : "outline"}
                        size="sm"
                        onClick={() => setCurrentPage(pageNum)}
                        className="w-8 h-8 p-0"
                      >
                        {pageNum}
                      </Button>
                    )
                  })}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
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