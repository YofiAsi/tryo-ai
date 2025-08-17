// Main API Client exports

export * from './types'
export * from './enums'
export * from './base-client'
export * from './auth-client'
export * from './candidates-client'
export * from './job-positions-client'
export * from './admin-client'

import { BaseApiClient } from './base-client'
import { AuthClient } from './auth-client'
import { CandidatesClient } from './candidates-client'
import { JobPositionsClient } from './job-positions-client'
import { AdminClient } from './admin-client'

// Main API Client class that combines all clients
export class ApiClient extends BaseApiClient {
  public auth: AuthClient
  public candidates: CandidatesClient
  public jobPositions: JobPositionsClient
  public admin: AdminClient

  constructor(baseUrl?: string) {
    super(baseUrl)
    
    // Initialize all client modules
    this.auth = new AuthClient(baseUrl)
    this.candidates = new CandidatesClient(baseUrl)
    this.jobPositions = new JobPositionsClient(baseUrl)
    this.admin = new AdminClient(baseUrl)
  }

  // Override setToken to update all client instances
  setToken(token: string) {
    super.setToken(token)
    this.auth.setToken(token)
    this.candidates.setToken(token)
    this.jobPositions.setToken(token)
    this.admin.setToken(token)
  }
}

// Create and export a default instance
export const apiClient = new ApiClient()

// Export individual clients for direct use if needed
export const authClient = new AuthClient()
export const candidatesClient = new CandidatesClient()
export const jobPositionsClient = new JobPositionsClient()
export const adminClient = new AdminClient()
