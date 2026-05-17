export * from './types'
export * from './enums'
export * from './base-client'
export * from './candidates-client'
export * from './job-positions-client'
export * from './ai-agents-client'
export * from './llm-client'

import { BaseApiClient } from './base-client'
import { CandidatesClient } from './candidates-client'
import { JobPositionsClient } from './job-positions-client'
import { AiAgentsClient } from './ai-agents-client'
import { LlmClient } from './llm-client'

export class ApiClient extends BaseApiClient {
  public candidates: CandidatesClient
  public jobPositions: JobPositionsClient
  public aiAgents: AiAgentsClient
  public llm: LlmClient

  constructor(baseUrl?: string) {
    super(baseUrl)

    this.candidates = new CandidatesClient(baseUrl)
    this.jobPositions = new JobPositionsClient(baseUrl)
    this.aiAgents = new AiAgentsClient(baseUrl)
    this.llm = new LlmClient(baseUrl)
  }
}

export const apiClient = new ApiClient()

export const candidatesClient = new CandidatesClient()
export const jobPositionsClient = new JobPositionsClient()
export const aiAgentsClient = new AiAgentsClient()
export const llmClient = new LlmClient()
