// API Types based on OpenAPI specification

import {
  CandidateStatus,
  JobStatus,
  EmploymentType,
  SeniorityLevel,
  WorkArrangement,
  JobTournamentStatus,
  TournamentCandidateStatus,
  DegreeType,
  LanguageLevel,
} from './enums'

export interface CandidateDTO {
  id: string
  name?: string
  gender?: string
  year_of_birth?: number
  city?: string
  country?: string
  email?: string
  phone?: string
  title?: string
  seniority_level?: SeniorityLevel
  status: CandidateStatus
  education?: Record<string, any>[]
  work_experience?: Record<string, any>[]
  certifications?: Record<string, any>[]
  skills?: Record<string, any>[]
  languages?: Record<string, any>[]
  keywords?: string[]
  links: Record<string, any>
  notes: Record<string, any>
  created_at: string
  updated_at: string
}

export interface JobPositionDTO {
  id: string
  title?: string
  company?: string
  city?: string
  country?: string
  employment_type?: EmploymentType
  seniority_level?: SeniorityLevel
  work_arrangement?: WorkArrangement
  responsibilities?: string[]
  recruiter_notes?: string
  salary?: number
  contact_email?: string
  contact_name?: string
  contact_phone?: string
  skills?: JobSkill[]
  requirements?: RequirementsOutput
  status: JobStatus
  original_text: string
  summary: string
  tournament: JobTournament
  created_at: string
  updated_at: string
}

export interface CreateCandidateDTO {
  name: string
  gender: string
  year_of_birth: number
  city: string
  country: string
  email: string
  phone: string
  title: string
  seniority_level: SeniorityLevel
}

export interface UpdateCandidateDTO {
  name?: string
  gender?: string
  year_of_birth?: number
  city?: string
  country?: string
  email?: string
  phone?: string
  title?: string
  seniority_level?: SeniorityLevel
}

export interface CreateJobPositionDTO {
  title: string
  original_text: string
  summary: string
  company: string
  city?: string
  country?: string
  employment_type: EmploymentType
  seniority_level: SeniorityLevel
  work_arrangement: WorkArrangement
  responsibilities?: string[]
  recruiter_notes?: string
  salary?: number
  contact_email?: string
  contact_name?: string
  contact_phone?: string
  skills?: JobSkill[]
  requirements?: RequirementsInput
}

export interface UpdateJobPositionDTO {
  title?: string
  company?: string
  city?: string
  country?: string
  employment_type?: EmploymentType
  seniority_level?: SeniorityLevel
  work_arrangement?: WorkArrangement
  responsibilities?: string[]
  recruiter_notes?: string
  salary?: number
  contact_email?: string
  contact_name?: string
  contact_phone?: string
  skills?: JobSkill[]
  requirements?: RequirementsInput
}

export interface ChangeCandidateStatusDTO {
  status: CandidateStatus
}

export interface JobSkill {
  name: string
  years_of_experience: number
  weight?: number
}

export interface RequirementsInput {
  certifications?: string[]
  educations?: EducationRequirement[]
  languages?: Language[]
}

export interface RequirementsOutput {
  certifications?: string[]
  educations?: EducationRequirement[]
  languages?: Language[]
}

export interface EducationRequirement {
  school?: string
  degree?: DegreeType
  field_of_study: string
}

export interface Language {
  name: string
  level: LanguageLevel
}

export interface JobTournament {
  status: JobTournamentStatus
  task: any
  candidates?: TournamentCandidate[]
}

export interface TournamentCandidate {
  candidate: CandidateDTO
  reasoning?: Reasoning[]
  status: TournamentCandidateStatus
  wins: number
  rank: number
}

export interface Reasoning {
  reason: string[]
  language: string
}

export interface JobPositionChatRequest {
  message: string
  message_history?: string
  model?: string
}

export interface JobPositionChatResponse {
  output: string
  message_history?: string
}

export interface JobPositionAnalyzeRequest {
  message_history: string
  model?: string
}

export interface LLMModel {
  id: string
}

export interface LLMCatalogResponse {
  models: LLMModel[]
  default_chat: string
  default_analyzer: string
}
