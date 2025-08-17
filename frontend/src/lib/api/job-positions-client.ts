// Job Positions API Client

import { BaseApiClient } from './base-client'
import type {
  JobPositionDTO,
  CreateJobPositionDTO,
  UpdateJobPositionDTO
} from './types'
import { JobStatus, EmploymentType, SeniorityLevel } from './enums'

export class JobPositionsClient extends BaseApiClient {
  // Get all job positions with pagination
  async getJobPositions(page: number = 1, size: number = 10): Promise<JobPositionDTO[]> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    return this.request<JobPositionDTO[]>(`/api/v1/job-positions/?${params}`)
  }

  // Create a new job position
  async createJobPosition(data: CreateJobPositionDTO): Promise<JobPositionDTO> {
    return this.request<JobPositionDTO>('/api/v1/job-positions/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Get job position by ID
  async getJobPosition(id: string): Promise<JobPositionDTO> {
    return this.request<JobPositionDTO>(`/api/v1/job-positions/${id}`)
  }

  // Update job position
  async updateJobPosition(id: string, data: UpdateJobPositionDTO): Promise<JobPositionDTO> {
    return this.request<JobPositionDTO>(`/api/v1/job-positions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  // Delete job position
  async deleteJobPosition(id: string): Promise<void> {
    return this.request<void>(`/api/v1/job-positions/${id}`, {
      method: 'DELETE',
    })
  }

  // Change job position status
  async changeJobPositionStatus(id: string, newStatus: JobStatus): Promise<JobPositionDTO> {
    return this.request<JobPositionDTO>(`/api/v1/job-positions/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ new_status: newStatus }),
    })
  }

  // Search job positions by text
  async searchJobPositions(
    query: string,
    page: number = 1,
    size: number = 10
  ): Promise<JobPositionDTO[]> {
    const params = new URLSearchParams({
      q: query,
      page: page.toString(),
      size: size.toString(),
    })
    return this.request<JobPositionDTO[]>(`/api/v1/job-positions/search?${params}`)
  }

  // Get job positions by status
  async getJobPositionsByStatus(
    status: JobStatus,
    page: number = 1,
    size: number = 10
  ): Promise<JobPositionDTO[]> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    return this.request<JobPositionDTO[]>(`/api/v1/job-positions/by-status/${status}?${params}`)
  }

  // Get job positions by employment type
  async getJobPositionsByEmploymentType(
    employmentType: EmploymentType,
    page: number = 1,
    size: number = 10
  ): Promise<JobPositionDTO[]> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    return this.request<JobPositionDTO[]>(`/api/v1/job-positions/by-employment-type/${employmentType}?${params}`)
  }

  // Get job positions by seniority level
  async getJobPositionsBySeniorityLevel(
    seniorityLevel: SeniorityLevel,
    page: number = 1,
    size: number = 10
  ): Promise<JobPositionDTO[]> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    return this.request<JobPositionDTO[]>(`/api/v1/job-positions/by-seniority-level/${seniorityLevel}?${params}`)
  }

  // Get job positions by location
  async getJobPositionsByLocation(
    city?: string,
    country?: string,
    page: number = 1,
    size: number = 10
  ): Promise<JobPositionDTO[]> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    
    if (city) params.append('city', city)
    if (country) params.append('country', country)
    
    return this.request<JobPositionDTO[]>(`/api/v1/job-positions/by-location?${params}`)
  }

  // Count job positions
  async countJobPositions(query?: string): Promise<{ count: number }> {
    const params = query ? `?query=${encodeURIComponent(query)}` : ''
    return this.request<{ count: number }>(`/api/v1/job-positions/count${params}`)
  }
}
