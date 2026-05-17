import { apiClient } from './index'
import type {
  CreateCandidateDTO,
  UpdateCandidateDTO,
  CreateJobPositionDTO,
  UpdateJobPositionDTO,
} from './types'
import { CandidateStatus } from './enums'

export const swrFetcher = {
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
}

export const swrKeys = {
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
}

export const defaultSWRConfig = {
  errorRetryCount: 3,
  errorRetryInterval: 5000,
  refreshInterval: 30000,
  revalidateOnFocus: false,
  revalidateOnReconnect: true,
  revalidateOnMount: true,
  dedupingInterval: 60000,
  keepPreviousData: true,
}
