// LLM catalog API Client

import { BaseApiClient } from './base-client'
import type { LLMCatalogResponse } from './types'

export class LlmClient extends BaseApiClient {
  async listModels(): Promise<LLMCatalogResponse> {
    return this.request<LLMCatalogResponse>('/api/v1/llm/models', {
      method: 'GET',
    })
  }
}
