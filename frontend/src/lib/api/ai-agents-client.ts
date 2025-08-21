// AI Agents API Client

import { BaseApiClient } from './base-client'
import type {
  JobPositionChatRequest,
  JobPositionChatResponse
} from './types'

export class AiAgentsClient extends BaseApiClient {
  constructor(baseUrl?: string) {
    // Set timeout to 120 seconds (120000ms) for AI agents
    super(baseUrl, 120000)
  }

  // Chat with job position analyzer agent
  async chatWithJobPosition(data: JobPositionChatRequest): Promise<JobPositionChatResponse> {
    return this.request<JobPositionChatResponse>('/api/v1/ai-agents/job-position/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }
}
