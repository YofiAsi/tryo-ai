import { apiClient } from './index'
import type { 
  CreateUserDTO, 
  CreateCandidateDTO,
  UpdateCandidateDTO,
  CreateJobPositionDTO,
  UpdateJobPositionDTO,
  CreateActivityLogDTO,
  UpdateActivityLogDTO,
  CreateTaskDTO
} from './types'
import { CandidateStatus } from './enums'

// SWR Fetcher Functions
export const swrFetcher = {
  // Auth
  auth: {
    currentUser: async () => {
      // Ensure token is set before making request
      const token = localStorage.getItem("auth_token")
      if (!token) {
        throw new Error("No auth token available")
      }
      return apiClient.auth.getCurrentUser()
    },
    logout: () => apiClient.auth.logout(),
  },

  // Candidates
  candidates: {
    list: (page: number = 1, size: number = 10) => 
      apiClient.candidates.getCandidates(page, size),
    create: (data: CreateCandidateDTO) => 
      apiClient.candidates.createCandidate(data),
    update: (id: string, data: UpdateCandidateDTO) => 
      apiClient.candidates.updateCandidate(id, data),
    delete: (id: string) => 
      apiClient.candidates.deleteCandidate(id),
    changeStatus: (id: string, status: CandidateStatus) => 
      apiClient.candidates.changeCandidateStatus(id, status),
    search: (query: string, page: number = 1, size: number = 10) => 
      apiClient.candidates.findCandidatesBySkills([query], page, size),
    getById: (id: string) => 
      apiClient.candidates.getCandidate(id),
  },

  // Job Positions
  jobPositions: {
    list: (page: number = 1, size: number = 10) => 
      apiClient.jobPositions.getJobPositions(page, size),
    create: (data: CreateJobPositionDTO) => 
      apiClient.jobPositions.createJobPosition(data),
    update: (id: string, data: UpdateJobPositionDTO) => 
      apiClient.jobPositions.updateJobPosition(id, data),
    delete: (id: string) => 
      apiClient.jobPositions.deleteJobPosition(id),
    search: (query: string, page: number = 1, size: number = 10) => 
      apiClient.jobPositions.searchJobPositions(query, page, size),
    getById: (id: string) => 
      apiClient.jobPositions.getJobPosition(id),
  },

  // Admin
  admin: {
    users: {
      list: (page: number = 1, size: number = 100) => 
        apiClient.admin.getUsers(page, size),
      create: (data: CreateUserDTO) => 
        apiClient.admin.createUser(data),
      changeStatus: (id: string, isActive: boolean) => 
        apiClient.admin.changeUserActiveStatus(id, isActive),
      update: (id: string, data: Partial<CreateUserDTO>) =>
        apiClient.admin.updateUser(id, data),
      delete: (id: string) =>
        apiClient.admin.deleteUser(id),
    },
    
    activityLogs: {
      list: (filters: {
        user_id?: string
        activity_type?: string
        start_date?: string
        end_date?: string
        ip_address?: string
        page?: number
        size?: number
      } = {}) => apiClient.admin.getActivityLogs(filters),
      
      summary: (days: number = 30) => 
        apiClient.admin.getActivitySummary(days),
      
      byUser: (userId: string, page: number = 1, size: number = 10) => 
        apiClient.admin.getUserActivityLogs(userId, page, size),
      
      create: (data: CreateActivityLogDTO) => 
        apiClient.admin.createActivityLog(data),
      
      update: (id: string, data: UpdateActivityLogDTO) => 
        apiClient.admin.updateActivityLog(id, data),
      
      delete: (id: string) => 
        apiClient.admin.deleteActivityLog(id),
    },

    tasks: {
      list: (page: number = 1, size: number = 10) => 
        apiClient.admin.getTasks(page, size),
      create: (data: CreateTaskDTO) => 
        apiClient.admin.createTask(data),
      getById: (id: string) => 
        apiClient.admin.getTask(id),
      delete: (id: string) => 
        apiClient.admin.deleteTask(id),
      getStatus: (id: string) => 
        apiClient.admin.getTaskStatus(id),
    },
  },
}

// SWR Keys for consistent caching
export const swrKeys = {
  auth: {
    currentUser: 'auth/current-user',
  },
  
  candidates: {
    list: (page: number, size: number) => `candidates/list?page=${page}&size=${size}`,
    search: (query: string, page: number, size: number) => `candidates/search?q=${query}&page=${page}&size=${size}`,
    byId: (id: string) => `candidates/${id}`,
  },
  
  jobPositions: {
    list: (page: number, size: number) => `job-positions/list?page=${page}&size=${size}`,
    search: (query: string, page: number, size: number) => `job-positions/search?q=${query}&page=${page}&size=${size}`,
    byId: (id: string) => `job-positions/${id}`,
  },
  
  admin: {
    users: {
      list: (page: number = 1, size: number = 100) => 
        `admin/users?page=${page}&size=${size}`,
      byId: (id: string) => `admin/users/${id}`,
      update: (id: string) => `admin/users/${id}`,
      delete: (id: string) => `admin/users/${id}`,
    },
    
    activityLogs: {
      list: (filters: Record<string, any>) => `admin/activity-logs?${new URLSearchParams(filters).toString()}`,
      summary: (days: number) => `admin/activity-summary?days=${days}`,
      byUser: (userId: string, page: number, size: number) => `admin/activity-logs/user/${userId}?page=${page}&size=${size}`,
    },
    
    tasks: {
      list: (page: number, size: number) => `admin/tasks?page=${page}&size=${size}`,
      byId: (id: string) => `admin/tasks/${id}`,
    },
  },
}

// Default SWR configuration
export const defaultSWRConfig = {
  errorRetryCount: 3,
  errorRetryInterval: 5000,
  refreshInterval: 30000, // 30 seconds
  revalidateOnFocus: false, // Don't revalidate on focus to prevent duplicate requests
  revalidateOnReconnect: true, // Revalidate when network reconnects
  revalidateOnMount: true, // Always revalidate on mount (page reload)
  dedupingInterval: 60000, // 60 seconds - more aggressive deduplication
  keepPreviousData: true,
}

// Auth-specific SWR configuration
export const authSWRConfig = {
  ...defaultSWRConfig,
  revalidateOnFocus: false, // Never revalidate auth on focus
  revalidateOnMount: true, // Always revalidate on mount
  dedupingInterval: 30000, // 30 seconds deduplication for auth
  errorRetryCount: 1, // Only retry once for auth
}
