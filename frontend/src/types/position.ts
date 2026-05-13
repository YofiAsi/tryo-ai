export interface Position {
  id: number
  title: string
  company: string
  department: string
  location: string
  status: "open" | "in-progress" | "on-hold" | "closed"
  datePosted: string
  description?: string
}

export interface JobPositionFormData {
  jobTitle: string
  company: string
  summary: string
  location: {
    country: string
    town: string
  }
  remoteWork: boolean
  semiRemote: boolean
  employmentType: string
  experienceLevel: string
  yearsOfExperience: number
  skills: Array<{
    name: string
    years: number
    weight: number
  }>
  languages: string[]
  educationRequirements: string
  certifications: string[]
  responsibilities: string
  recruiterNotes: string
  contactInfo: {
    name: string
    email: string
    phone: string
  }
}

export interface FormErrors {
  jobTitle?: string
  company?: string
  summary?: string
  country?: string
  town?: string
  skills?: string
  responsibilities?: string
  contactName?: string
  contactEmail?: string
  contactPhone?: string
} 