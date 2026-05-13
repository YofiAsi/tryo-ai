import useSWR, { mutate } from 'swr'
import { swrFetcher, swrKeys, defaultSWRConfig } from '@/lib/api/swr-fetcher'
import type { 
  UserDTO, 
  CreateUserDTO, 
  CandidateDTO, 
  CreateCandidateDTO, 
  UpdateCandidateDTO,
  JobPositionDTO,
  CreateJobPositionDTO,
  UpdateJobPositionDTO,
  CreateActivityLogDTO,
  BaseTaskDTO,
  CreateTaskDTO
} from '@/lib/api/types'
import { CandidateStatus } from '@/lib/api/enums'

// Utility function to revalidate all data
export const revalidateAllData = async () => {
  try {
    // Revalidate all SWR keys
    await Promise.all([
      mutate((key: string) => key.startsWith('candidates'), undefined, { revalidate: true }),
      mutate((key: string) => key.startsWith('job-positions'), undefined, { revalidate: true }),
      mutate((key: string) => key.startsWith('admin'), undefined, { revalidate: true }),
    ])
  } catch (error) {
    console.error('Failed to revalidate all data:', error)
  }
}

// Candidate Hooks
export function useCandidates(page: number = 1, size: number = 10) {
  const key = swrKeys.candidates.list(page, size)
  return useSWR(key, () => swrFetcher.candidates.list(page, size), defaultSWRConfig)
}

export function useCandidate(id: string) {
  const key = swrKeys.candidates.byId(id)
  return useSWR(
    id ? key : null, 
    () => swrFetcher.candidates.getById(id), 
    defaultSWRConfig
  )
}

export function useCandidateSearch(query: string, page: number = 1, size: number = 10) {
  const key = swrKeys.candidates.search(query, page, size)
  return useSWR(
    query ? key : null,
    () => swrFetcher.candidates.search(query, page, size),
    defaultSWRConfig
  )
}

// Job Position Hooks
export function useJobPositions(page: number = 1, size: number = 10) {
  const key = swrKeys.jobPositions.list(page, size)
  return useSWR(key, () => swrFetcher.jobPositions.list(page, size), defaultSWRConfig)
}

export function useJobPosition(id: string) {
  const key = swrKeys.jobPositions.byId(id)
  return useSWR(
    id ? key : null,
    () => swrFetcher.jobPositions.getById(id),
    defaultSWRConfig
  )
}

export function useJobPositionSearch(query: string, page: number = 1, size: number = 10) {
  const key = swrKeys.jobPositions.search(query, page, size)
  return useSWR(
    query ? key : null,
    () => swrFetcher.jobPositions.search(query, page, size),
    defaultSWRConfig
  )
}

// Admin Hooks
export function useAdminUsers(page: number = 1, size: number = 100) {
  const key = swrKeys.admin.users.list(page, size)
  return useSWR(key, () => swrFetcher.admin.users.list(page, size), defaultSWRConfig)
}

export function useActivityLogs(filters: Record<string, any> = {}) {
  const key = swrKeys.admin.activityLogs.list(filters)
  return useSWR(key, () => swrFetcher.admin.activityLogs.list(filters), defaultSWRConfig)
}

export function useActivitySummary(days: number = 30) {
  const key = swrKeys.admin.activityLogs.summary(days)
  return useSWR(key, () => swrFetcher.admin.activityLogs.summary(days), defaultSWRConfig)
}

export function useUserActivityLogs(userId: string, page: number = 1, size: number = 10) {
  const key = swrKeys.admin.activityLogs.byUser(userId, page, size)
  return useSWR(
    userId ? key : null,
    () => swrFetcher.admin.activityLogs.byUser(userId, page, size),
    defaultSWRConfig
  )
}

export function useAdminTasks(page: number = 1, size: number = 10) {
  const key = swrKeys.admin.tasks.list(page, size)
  return useSWR(key, () => swrFetcher.admin.tasks.list(page, size), defaultSWRConfig)
}

export function useAdminTask(id: string) {
  const key = swrKeys.admin.tasks.byId(id)
  return useSWR(
    id ? key : null,
    () => swrFetcher.admin.tasks.getById(id),
    defaultSWRConfig
  )
}

// Mutation Hooks
export function useCandidateMutations() {
  const createCandidate = async (data: CreateCandidateDTO) => {
    const newCandidate = await swrFetcher.candidates.create(data)
    
    // Optimistically update the candidates list
    mutate(
      (key: string) => key.startsWith('candidates/list'),
      (candidates: CandidateDTO[] = []) => [newCandidate, ...candidates],
      false
    )
    
    return newCandidate
  }

  const updateCandidate = async (id: string, data: UpdateCandidateDTO) => {
    const updatedCandidate = await swrFetcher.candidates.update(id, data)
    
    // Update both the list and individual candidate
    mutate(
      (key: string) => key.startsWith('candidates/list'),
      (candidates: CandidateDTO[] = []) => 
        candidates.map(c => c.id === id ? updatedCandidate : c),
      false
    )
    
    mutate(swrKeys.candidates.byId(id), updatedCandidate, false)
    
    return updatedCandidate
  }

  const deleteCandidate = async (id: string) => {
    await swrFetcher.candidates.delete(id)
    
    // Remove from lists
    mutate(
      (key: string) => key.startsWith('candidates/list'),
      (candidates: CandidateDTO[] = []) => 
        candidates.filter(c => c.id !== id),
      false
    )
    
    // Clear individual candidate cache
    mutate(swrKeys.candidates.byId(id), undefined, false)
  }

  const changeCandidateStatus = async (id: string, status: CandidateStatus) => {
    const updatedCandidate = await swrFetcher.candidates.changeStatus(id, status)
    
    // Update both the list and individual candidate
    mutate(
      (key: string) => key.startsWith('candidates/list'),
      (candidates: CandidateDTO[] = []) => 
        candidates.map(c => c.id === id ? updatedCandidate : c),
      false
    )
    
    mutate(swrKeys.candidates.byId(id), updatedCandidate, false)
    
    return updatedCandidate
  }

  return {
    createCandidate,
    updateCandidate,
    deleteCandidate,
    changeCandidateStatus,
  }
}

export function useJobPositionMutations() {
  const createJobPosition = async (data: CreateJobPositionDTO) => {
    const newPosition = await swrFetcher.jobPositions.create(data)
    
    // Optimistically update the positions list
    mutate(
      (key: string) => key.startsWith('job-positions/list'),
      (positions: JobPositionDTO[] = []) => [newPosition, ...positions],
      false
    )
    
    return newPosition
  }

  const updateJobPosition = async (id: string, data: UpdateJobPositionDTO) => {
    const updatedPosition = await swrFetcher.jobPositions.update(id, data)
    
    // Update both the list and individual position
    mutate(
      (key: string) => key.startsWith('job-positions/list'),
      (positions: JobPositionDTO[] = []) => 
        positions.map(p => p.id === id ? updatedPosition : p),
      false
    )
    
    mutate(swrKeys.jobPositions.byId(id), updatedPosition, false)
    
    return updatedPosition
  }

  const deleteJobPosition = async (id: string) => {
    await swrFetcher.jobPositions.delete(id)
    
    // Remove from lists
    mutate(
      (key: string) => key.startsWith('job-positions/list'),
      (positions: JobPositionDTO[] = []) => 
        positions.filter(p => p.id !== id),
      false
    )
    
    // Clear individual position cache
    mutate(swrKeys.jobPositions.byId(id), undefined, false)
  }

  return {
    createJobPosition,
    updateJobPosition,
    deleteJobPosition,
  }
}

export function useAdminMutations() {
  const createUser = async (data: CreateUserDTO) => {
    const newUser = await swrFetcher.admin.users.create(data)
    
    // Optimistically update the users list
    mutate(
      (key: string) => key.startsWith('admin/users'),
      (users: UserDTO[] = []) => [newUser, ...users],
      false
    )
    
    return newUser
  }

  const changeUserStatus = async (id: string, isActive: boolean) => {
    const updatedUser = await swrFetcher.admin.users.changeStatus(id, isActive)
    
    // Update both the list and individual user
    mutate(
      (key: string) => key.startsWith('admin/users'),
      (users: UserDTO[] = []) => 
        users.map(u => u.id === id ? updatedUser : u),
      false
    )
    
    return updatedUser
  }

  const updateUser = async (id: string, data: Partial<CreateUserDTO>) => {
    const updatedUser = await swrFetcher.admin.users.update(id, data)
    
    // Update both the list and individual user
    mutate(
      (key: string) => key.startsWith('admin/users'),
      (users: UserDTO[] = []) => 
        users.map(u => u.id === id ? updatedUser : u),
      false
    )
    
    return updatedUser
  }

  const deleteUser = async (id: string) => {
    await swrFetcher.admin.users.delete(id)
    
    // Remove from lists
    mutate(
      (key: string) => key.startsWith('admin/users'),
      (users: UserDTO[] = []) => 
        users.filter(u => u.id !== id),
      false
    )
  }

  const createActivityLog = async (data: CreateActivityLogDTO) => {
    const newLog = await swrFetcher.admin.activityLogs.create(data)
    
    // Invalidate activity log caches to refresh data
    mutate((key: string) => key.startsWith('admin/activity-logs'))
    
    return newLog
  }

  const createTask = async (data: CreateTaskDTO) => {
    const newTask = await swrFetcher.admin.tasks.create(data)
    
    // Optimistically update the tasks list
    mutate(
      (key: string) => key.startsWith('admin/tasks'),
      (tasks: BaseTaskDTO[] = []) => [newTask, ...tasks],
      false
    )
    
    return newTask
  }

  return {
    createUser,
    changeUserStatus,
    updateUser,
    deleteUser,
    createActivityLog,
    createTask,
  }
}
