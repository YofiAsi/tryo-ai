// API Types based on OpenAPI specification

import {
  UserRole,
  CandidateStatus,
  JobStatus,
  EmploymentType,
  SeniorityLevel,
  WorkArrangement,
  JobTournamentStatus,
  TournamentCandidateStatus,
  DegreeType,
  LanguageLevel,
  TaskType,
  TaskStatus,
  ActivityType
} from './enums'

export interface UserDTO {
  id: string
  name?: string
  email?: string
  role?: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
  last_login?: string
}

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

export interface CreateUserDTO {
  name: string
  email: string
  role: UserRole
}

export interface ChangeUserActiveStatusDTO {
  is_active: boolean
}

export interface ChangeCandidateStatusDTO {
  status: CandidateStatus
}

export interface GoogleAuthRequest {
  code: string
  state?: string
}

export interface GoogleLoginResponse {
  auth_url: string
  message: string
  expires_in?: number
  state?: string
}

export interface LoginResponse {
  user: AuthUserResponse
  token: TokenResponse
}

export interface LogoutResponse {
  message: string
  user_id: string
  email: string
  logged_out_at: string
}

export interface AuthUserResponse {
  id: string
  email: string
  name: string
  role: string
  picture?: string
  is_active: boolean
  auth_provider: string
  created_at: string
  updated_at: string
  last_login?: string
}

export interface TokenResponse {
  access_token: string
  token_type?: string
  expires_in: number
  refresh_token?: string
  scope?: string
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

// Admin types
export interface BaseTaskDTO {
  id: string
  type: TaskType
  status: TaskStatus
  progress_percentage?: number
  created_at?: string
  updated_at?: string
}

export interface TaskWithDataDTO {
  id: string
  type: TaskType
  status: TaskStatus
  progress_percentage?: number
  created_at?: string
  updated_at?: string
  data?: CVProcessingTaskDTO
}

export interface CVProcessingTaskDTO {
  candidates_ids: string[]
}

export interface CreateTaskDTO {
  type: TaskType
  data: CVProcessingTaskDTO
}

export interface ActivityLogDTO {
  id: string
  user?: UserDTO
  activity_type: ActivityType
  data?: Record<string, any>
  date: string
  ip_address?: string
  user_agent?: string
}

export interface CreateActivityLogDTO {
  user_id?: string
  activity_type: ActivityType
  data?: Record<string, any>
  ip_address?: string
  user_agent?: string
}

export interface UpdateActivityLogDTO {
  data?: Record<string, any>
  ip_address?: string
  user_agent?: string
}

export interface ActivityLogSummaryDTO {
  total_activities: number
  activities_by_type: Record<string, number>
  activities_by_user: Record<string, number>
  recent_activities: ActivityLogDTO[]
}

export interface JobPositionChatRequest {
  message: string
  message_history?: string
}

export interface JobPositionChatResponse {
  output: string
  message_history?: string
}
