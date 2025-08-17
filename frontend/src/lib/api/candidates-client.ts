// Candidates API Client

import { BaseApiClient } from './base-client'
import type {
  CandidateDTO,
  CreateCandidateDTO,
  UpdateCandidateDTO,

} from './types'
import { CandidateStatus, SeniorityLevel } from './enums'

export class CandidatesClient extends BaseApiClient {
  // Get all candidates with pagination
  async getCandidates(page: number = 1, size: number = 10): Promise<CandidateDTO[]> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    return this.request<CandidateDTO[]>(`/api/v1/candidates/?${params}`)
  }

  // Create a new candidate
  async createCandidate(data: CreateCandidateDTO): Promise<CandidateDTO> {
    return this.request<CandidateDTO>('/api/v1/candidates/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Get candidate by ID
  async getCandidate(id: string): Promise<CandidateDTO> {
    return this.request<CandidateDTO>(`/api/v1/candidates/${id}`)
  }

  // Update candidate
  async updateCandidate(id: string, data: UpdateCandidateDTO): Promise<CandidateDTO> {
    return this.request<CandidateDTO>(`/api/v1/candidates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  // Delete candidate
  async deleteCandidate(id: string): Promise<void> {
    return this.request<void>(`/api/v1/candidates/${id}`, {
      method: 'DELETE',
    })
  }

  // Change candidate status
  async changeCandidateStatus(id: string, status: CandidateStatus): Promise<CandidateDTO> {
    return this.request<CandidateDTO>(`/api/v1/candidates/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    })
  }

  // Find candidates by skills
  async findCandidatesBySkills(
    skills: string[],
    page: number = 1,
    size: number = 10
  ): Promise<CandidateDTO[]> {
    const params = new URLSearchParams({
      skills: skills.join(','),
      page: page.toString(),
      size: size.toString(),
    })
    return this.request<CandidateDTO[]>(`/api/v1/candidates/search/skills?${params}`)
  }

  // Find candidates by seniority level
  async findCandidatesBySeniority(
    seniorityLevel: SeniorityLevel,
    page: number = 1,
    size: number = 10
  ): Promise<CandidateDTO[]> {
    const params = new URLSearchParams({
      seniority_level: seniorityLevel,
      page: page.toString(),
      size: size.toString(),
    })
    return this.request<CandidateDTO[]>(`/api/v1/candidates/search/seniority?${params}`)
  }
}
