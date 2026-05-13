// API Enums based on OpenAPI specification

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user'
}

export enum CandidateStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export enum JobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  OPEN = 'open',
  CLOSED = 'closed',
  DRAFT = 'draft',
  ARCHIVED = 'archived'
}

export enum EmploymentType {
  FULL_TIME = 'full-time',
  PART_TIME = 'part-time',
  CONTRACT = 'contract',
  INTERNSHIP = 'internship',
  FREELANCE = 'freelance'
}

export enum SeniorityLevel {
  JUNIOR = 'Junior',
  MID = 'Mid',
  SENIOR = 'Senior',
  LEAD = 'Lead',
  PRINCIPAL = 'Principal'
}

export enum WorkArrangement {
  REMOTE = 'remote',
  HYBRID = 'hybrid',
  ON_SITE = 'on-site'
}

export enum JobTournamentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export enum TournamentCandidateStatus {
  UNCHECKED = 'unchecked',
  CHECKED = 'checked',
  APPROVED = 'approved',
  HIDDEN = 'hidden',
  REJECTED = 'rejected',
  INTERVIEWED = 'interviewed'
}

export enum DegreeType {
  ASSOCIATE = 'associate',
  BACHELOR = 'bachelor',
  MASTER = 'master',
  DOCTORATE = 'doctorate',
  DIPLOMA = 'diploma'
}

export enum LanguageLevel {
  NATIVE = 'native',
  FLUENT = 'fluent',
  ADVANCED = 'advanced',
  INTERMEDIATE = 'intermediate',
  BASIC = 'basic'
}

export enum TaskType {
  CV_PROCESSING = 'cv_processing'
}

export enum TaskStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export enum ActivityType {
  LOGIN = 'login',
  LOGOUT = 'logout',
  NEW_CANDIDATE = 'new_candidate',
  UPDATE_CANDIDATE = 'update_candidate',
  DELETE_CANDIDATE = 'delete_candidate',
  NEW_JOB_POSITION = 'new_job_position',
  UPDATE_JOB_POSITION = 'update_job_position',
  DELETE_JOB_POSITION = 'delete_job_position',
  CHANGE_CANDIDATE_STATUS = 'change_candidate_status',
  CHANGE_JOB_POSITION_STATUS = 'change_job_position_status',
  USER_CREATED = 'user_created',
  USER_UPDATED = 'user_updated',
  USER_DEACTIVATED = 'user_deactivated',
  TASK_CREATED = 'task_created',
  TASK_UPDATED = 'task_updated',
  TASK_COMPLETED = 'task_completed',
  TASK_FAILED = 'task_failed',
  SYSTEM_EVENT = 'system_event',
  ERROR_EVENT = 'error_event'
}
