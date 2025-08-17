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