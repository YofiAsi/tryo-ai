// Admin API Client

import { BaseApiClient } from './base-client'
import type {
  UserDTO,
  CreateUserDTO,

  BaseTaskDTO,
  TaskWithDataDTO,
  CreateTaskDTO,
  ActivityLogDTO,
  CreateActivityLogDTO,
  UpdateActivityLogDTO,
  ActivityLogSummaryDTO
} from './types'

export class AdminClient extends BaseApiClient {
  // User management
  async getUsers(page: number = 1, size: number = 10): Promise<UserDTO[]> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    return this.request<UserDTO[]>(`/api/v1/admin/users?${params}`)
  }

  async createUser(data: CreateUserDTO): Promise<UserDTO> {
    return this.request<UserDTO>('/api/v1/admin/users', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async changeUserActiveStatus(id: string, isActive: boolean): Promise<UserDTO> {
    return this.request<UserDTO>(`/api/v1/admin/users/${id}/active-status`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: isActive }),
    })
  }

  async updateUser(id: string, data: Partial<CreateUserDTO>): Promise<UserDTO> {
    return this.request<UserDTO>(`/api/v1/admin/users/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteUser(id: string): Promise<void> {
    return this.request<void>(`/api/v1/admin/users/${id}`, {
      method: 'DELETE',
    })
  }

  // Task management
  async getTasks(page: number = 1, size: number = 10): Promise<BaseTaskDTO[]> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    return this.request<BaseTaskDTO[]>(`/api/v1/admin/tasks?${params}`)
  }

  async createTask(data: CreateTaskDTO): Promise<TaskWithDataDTO> {
    return this.request<TaskWithDataDTO>('/api/v1/admin/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getTask(id: string): Promise<TaskWithDataDTO> {
    return this.request<TaskWithDataDTO>(`/api/v1/admin/tasks/${id}`)
  }

  async deleteTask(id: string): Promise<void> {
    return this.request<void>(`/api/v1/admin/tasks/${id}`, {
      method: 'DELETE',
    })
  }

  async getTaskStatus(id: string): Promise<Record<string, any>> {
    return this.request<Record<string, any>>(`/api/v1/admin/tasks/${id}/status`)
  }

  // Activity logs
  async getActivityLogs(
    filters: {
      user_id?: string
      activity_type?: string
      start_date?: string
      end_date?: string
      ip_address?: string
      page?: number
      size?: number
    } = {}
  ): Promise<{ data: ActivityLogDTO[]; totalCount: number }> {
    const params = new URLSearchParams()
    
    if (filters.user_id) params.append('user_id', filters.user_id)
    if (filters.activity_type) params.append('activity_type', filters.activity_type)
    if (filters.start_date) params.append('start_date', filters.start_date)
    if (filters.end_date) params.append('end_date', filters.end_date)
    if (filters.ip_address) params.append('ip_address', filters.ip_address)
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.size) params.append('size', filters.size.toString())

    const { data, headers } = await this.requestWithHeaders<ActivityLogDTO[]>(`/api/v1/admin/activity-logs?${params}`)
    
    // Extract total count from X-Total-Count header
    const totalCount = parseInt(headers.get('X-Total-Count') || '0', 10)
    
    return { data, totalCount }
  }

  async createActivityLog(data: CreateActivityLogDTO): Promise<ActivityLogDTO> {
    return this.request<ActivityLogDTO>('/api/v1/admin/activity-logs', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getActivityLog(id: string): Promise<ActivityLogDTO> {
    return this.request<ActivityLogDTO>(`/api/v1/admin/activity-logs/${id}`)
  }

  async updateActivityLog(id: string, data: UpdateActivityLogDTO): Promise<ActivityLogDTO> {
    return this.request<ActivityLogDTO>(`/api/v1/admin/activity-logs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteActivityLog(id: string): Promise<void> {
    return this.request<void>(`/api/v1/admin/activity-logs/${id}`, {
      method: 'DELETE',
    })
  }

  async getUserActivityLogs(
    userId: string,
    page: number = 1,
    size: number = 10
  ): Promise<{ data: ActivityLogDTO[]; totalCount: number }> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    const { data, headers } = await this.requestWithHeaders<ActivityLogDTO[]>(`/api/v1/admin/activity-logs/user/${userId}?${params}`)
    
    // Extract total count from X-Total-Count header
    const totalCount = parseInt(headers.get('X-Total-Count') || '0', 10)
    
    return { data, totalCount }
  }

  async getActivitySummary(days: number = 30): Promise<ActivityLogSummaryDTO> {
    const params = new URLSearchParams({
      days: days.toString(),
    })
    return this.request<ActivityLogSummaryDTO>(`/api/v1/admin/activity-logs/summary/statistics?${params}`)
  }

  async cleanupOldLogs(days: number = 90): Promise<void> {
    const params = new URLSearchParams({
      days: days.toString(),
    })
    return this.request<void>(`/api/v1/admin/activity-logs/cleanup/old-logs?${params}`, {
      method: 'POST',
    })
  }
}
