"use client"

import { motion } from "framer-motion"
import { ArrowLeft, Building2, Calendar, MapPin, Loader2 } from "lucide-react"
import { Link, useParams, useNavigate } from "react-router-dom"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { MatchedCandidatesTable } from "./matched-candidates-table"
import { getMatchedCandidates } from "@/lib/candidate-matching"
import { useJobPosition } from "@/hooks/use-swr-hooks"

import { JobStatus } from "@/lib/api/enums"

const statusVariants: Record<JobStatus, "default" | "secondary" | "outline" | "destructive"> = {
  [JobStatus.OPEN]: "default",
  [JobStatus.PROCESSING]: "secondary",
  [JobStatus.PENDING]: "outline",
  [JobStatus.COMPLETED]: "outline",
  [JobStatus.FAILED]: "destructive",
  [JobStatus.CLOSED]: "destructive",
  [JobStatus.DRAFT]: "outline",
  [JobStatus.ARCHIVED]: "outline",
}

const statusLabels: Record<JobStatus, string> = {
  [JobStatus.OPEN]: "Open",
  [JobStatus.PROCESSING]: "In Progress",
  [JobStatus.PENDING]: "Pending",
  [JobStatus.COMPLETED]: "Completed",
  [JobStatus.FAILED]: "Failed",
  [JobStatus.CLOSED]: "Closed",
  [JobStatus.DRAFT]: "Draft",
  [JobStatus.ARCHIVED]: "Archived",
}

const pageVariants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: "easeOut" as const,
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3,
      ease: "easeIn" as const,
    },
  },
}

const cardVariants = {
  hidden: {
    opacity: 0,
    y: 30,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut" as const,
    },
  },
  hover: {
    y: -2,
    boxShadow: "0 10px 25px rgba(0, 0, 0, 0.1)",
    transition: {
      duration: 0.3,
      ease: "easeOut" as const,
    },
  },
}

const headerVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.5,
      ease: "easeOut" as const,
    },
  },
}

const badgeVariants = {
  hidden: { opacity: 0, scale: 0.8, rotate: -10 },
  visible: {
    opacity: 1,
    scale: 1,
    rotate: 0,
    transition: {
      duration: 0.4,
      ease: "easeOut" as const,
      delay: 0.3,
    },
  },
  hover: {
    scale: 1.05,
    rotate: 2,
    transition: {
      duration: 0.2,
    },
  },
}

const infoItemVariants = {
  hidden: { opacity: 0, x: -10 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3,
      ease: "easeOut" as const,
    },
  },
  hover: {
    x: 4,
    transition: {
      duration: 0.2,
    },
  },
}

const buttonVariants = {
  hover: {
    scale: 1.05,
    transition: {
      duration: 0.2,
      ease: "easeInOut" as const,
    },
  },
  tap: {
    scale: 0.95,
    transition: {
      duration: 0.1,
    },
  },
}

export function PositionDetailsPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const { data: position, error, isLoading } = useJobPosition(id || "")
  
  if (isLoading) {
    return (
      <SidebarInset>
        <div className="flex h-full items-center justify-center">
          <div className="flex items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <span className="text-lg text-gray-600">Loading position details...</span>
          </div>
        </div>
      </SidebarInset>
    )
  }

  if (error || !position) {
    return (
      <SidebarInset>
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-red-100 mx-auto mb-4">
              <svg className="h-10 w-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Position</h2>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              {error?.message || "Position not found"}
            </p>
            <Button 
              size="lg"
              onClick={() => navigate("/")}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Back to Positions
            </Button>
          </div>
        </div>
      </SidebarInset>
    )
  }

  const matchedCandidates = getMatchedCandidates()

  return (
    <SidebarInset>
      <motion.header
        className="flex h-16 shrink-0 items-center gap-2 border-b px-4"
        variants={headerVariants}
        initial="hidden"
        animate="visible"
      >
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        <motion.div variants={buttonVariants} whileHover="hover" whileTap="tap">
          <Button variant="ghost" size="sm" asChild className="gap-2">
            <Link to="/">
              <ArrowLeft className="h-4 w-4" />
              Back to Positions
            </Link>
          </Button>
        </motion.div>
        <Separator orientation="vertical" className="h-4" />
        <motion.div
          className="flex flex-col"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <h1 className="text-lg font-semibold">{position.title || "Untitled Position"}</h1>
          <p className="text-sm text-muted-foreground">{position.company || "Company not specified"}</p>
        </motion.div>
      </motion.header>

      <motion.div
        className="flex flex-1 flex-col gap-6 p-6"
        variants={pageVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        {/* Position Overview */}
        <motion.div className="grid gap-6 md:grid-cols-1" variants={cardVariants} whileHover="hover">
          <div className="md:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2, duration: 0.5 }}
                  >
                    <CardTitle className="text-2xl">{position.title || "Untitled Position"}</CardTitle>
                    <CardDescription className="text-base mt-1">
                      {position.seniority_level || "Not specified"} • {position.company || "Company not specified"}
                    </CardDescription>
                  </motion.div>
                  <motion.div variants={badgeVariants} initial="hidden" animate="visible" whileHover="hover">
                    <Badge variant={statusVariants[position.status as JobStatus]} className="text-sm">
                      {statusLabels[position.status as JobStatus]}
                    </Badge>
                  </motion.div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <motion.div
                  className="flex flex-wrap gap-4 text-sm text-muted-foreground"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                >
                  {position.city && (
                    <motion.div className="flex items-center gap-1" variants={infoItemVariants} whileHover="hover">
                      <MapPin className="h-4 w-4" />
                      {position.city}{position.country && `, ${position.country}`}
                    </motion.div>
                  )}
                  <motion.div className="flex items-center gap-1" variants={infoItemVariants} whileHover="hover">
                    <Calendar className="h-4 w-4" />
                    Posted {new Date(position.created_at).toLocaleDateString()}
                  </motion.div>
                  {position.employment_type && (
                    <motion.div className="flex items-center gap-1" variants={infoItemVariants} whileHover="hover">
                      <Building2 className="h-4 w-4" />
                      {position.employment_type}
                    </motion.div>
                  )}
                </motion.div>
              </CardContent>
            </Card>
          </div>
        </motion.div>

        {/* Job Description and Requirements */}
        <motion.div className="grid gap-6 md:grid-cols-1" variants={cardVariants} whileHover="hover">
          <Card>
            <CardHeader>
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.4 }}
              >
                <CardTitle>Job Description</CardTitle>
              </motion.div>
            </CardHeader>
            <CardContent>
              <motion.p
                className="text-muted-foreground leading-relaxed"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5, duration: 0.6 }}
              >
                {position.summary || position.original_text || "No description available for this position."}
              </motion.p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Matched Candidates Table */}
        <motion.div variants={cardVariants} whileHover="hover">
          <Card>
            <CardHeader>
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.4 }}
              >
                <CardTitle>Matched Candidates</CardTitle>
                <CardDescription>Candidates ranked by compatibility with this position</CardDescription>
              </motion.div>
            </CardHeader>
            <CardContent className="p-0">
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6, duration: 0.5 }}>
                <MatchedCandidatesTable candidates={matchedCandidates} />
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </SidebarInset>
  )
} 