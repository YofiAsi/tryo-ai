// API Enums based on OpenAPI specification

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

