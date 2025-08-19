"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ArrowLeft, ArrowRight, Plus, X, Building2, Sparkles, Loader2, FileText, MapPin, Briefcase, GraduationCap, User, Mail, Phone, Wand2 } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { Slider } from "@/components/ui/slider"
import { JobPositionsClient } from "@/lib/api/job-positions-client"
import { CreateJobPositionDTO } from "@/lib/api/types"
import { EmploymentType, SeniorityLevel, WorkArrangement } from "@/lib/api/enums"
import { useToast } from "@/components/ui/use-toast"
import { Toaster } from "@/components/ui/toaster"

interface JobSkill {
  name: string
  years: number
  weight: number
}

interface JobFormData {
  // Step 1: Job Summary
  jobSummary: string
  
  // Step 2: Review & Edit
  jobTitle: string
  company: string
  summary: string
  location: {
    country: string
    town: string
  }
  remoteWork: boolean
  semiRemote: boolean
  employmentType: "full-time" | "part-time" | "contract" | "internship" | "freelance"
  experienceLevel: "junior" | "mid" | "senior" | "lead" | "principal"
  yearsOfExperience: number
  skills: JobSkill[]
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

const initialFormData: JobFormData = {
  jobSummary: "",
  jobTitle: "",
  company: "",
  summary: "",
  location: {
    country: "",
    town: ""
  },
  remoteWork: false,
  semiRemote: false,
  employmentType: "full-time",
  experienceLevel: "mid",
  yearsOfExperience: 3,
  skills: [],
  languages: [],
  educationRequirements: "",
  certifications: [],
  responsibilities: "",
  recruiterNotes: "",
  contactInfo: {
    name: "",
    email: "",
    phone: ""
  }
}

const stepVariants = {
  hidden: { opacity: 0, x: 20 },
  visible: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 }
}

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export function AddPositionPage() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<JobFormData>(initialFormData)
  const [newSkill, setNewSkill] = useState({ name: "", years: 1, weight: 3 })
  const [newLanguage, setNewLanguage] = useState("")
  const [newCertification, setNewCertification] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const { toast } = useToast()
  const jobPositionsClient = new JobPositionsClient()

  const handleNext = () => {
    if (currentStep < 2) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const updateFormData = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    // Clear error when field is updated
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const updateNestedFormData = (parent: keyof JobFormData, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [parent]: {
        ...(prev[parent] as any),
        [field]: value
      }
    }))
    // Clear error when nested field is updated
    const errorKey = parent === 'location' ? (field === 'country' ? 'country' : 'town') : 
                    parent === 'contactInfo' ? (field === 'name' ? 'contactName' : field === 'email' ? 'contactEmail' : 'contactPhone') : ''
    if (errorKey && errors[errorKey]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[errorKey]
        return newErrors
      })
    }
  }

  const addSkill = () => {
    if (newSkill.name.trim()) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, newSkill]
      }))
      setNewSkill({ name: "", years: 1, weight: 3 })
    }
  }

  const removeSkill = (index: number) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter((_, i) => i !== index)
    }))
  }

  const addLanguage = () => {
    if (newLanguage.trim()) {
      setFormData(prev => ({
        ...prev,
        languages: [...prev.languages, newLanguage.trim()]
      }))
      setNewLanguage("")
    }
  }

  const removeLanguage = (index: number) => {
    setFormData(prev => ({
      ...prev,
      languages: prev.languages.filter((_, i) => i !== index)
    }))
  }

  const addCertification = () => {
    if (newCertification.trim()) {
      setFormData(prev => ({
        ...prev,
        certifications: [...prev.certifications, newCertification.trim()]
      }))
      setNewCertification("")
    }
  }

  const removeCertification = (index: number) => {
    setFormData(prev => ({
      ...prev,
      certifications: prev.certifications.filter((_, i) => i !== index)
    }))
  }

  // Helper functions to map form data to API format
  const mapExperienceLevelToSeniorityLevel = (level: string): SeniorityLevel => {
    switch (level) {
      case "junior": return SeniorityLevel.JUNIOR
      case "mid": return SeniorityLevel.MID
      case "senior": return SeniorityLevel.SENIOR
      case "lead": return SeniorityLevel.LEAD
      case "principal": return SeniorityLevel.PRINCIPAL
      default: return SeniorityLevel.MID
    }
  }

  const mapWorkArrangement = (remoteWork: boolean, semiRemote: boolean): WorkArrangement => {
    if (remoteWork) return WorkArrangement.REMOTE
    if (semiRemote) return WorkArrangement.HYBRID
    return WorkArrangement.ON_SITE
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    // Basic Information validation
    if (!formData.jobTitle.trim()) {
      newErrors.jobTitle = "Job title is required"
    }
    if (!formData.company.trim()) {
      newErrors.company = "Company name is required"
    }
    if (!formData.summary.trim()) {
      newErrors.summary = "Job summary is required"
    }
    if (!formData.location.country.trim()) {
      newErrors.country = "Country is required"
    }
    if (!formData.location.town.trim()) {
      newErrors.town = "Town/City is required"
    }
    if (!formData.responsibilities.trim()) {
      newErrors.responsibilities = "Job responsibilities are required"
    }
    
    // Contact Information validation
    if (!formData.contactInfo.name.trim()) {
      newErrors.contactName = "Contact name is required"
    }
    if (!formData.contactInfo.email.trim()) {
      newErrors.contactEmail = "Contact email is required"
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contactInfo.email)) {
      newErrors.contactEmail = "Please enter a valid email address"
    }
    if (!formData.contactInfo.phone.trim()) {
      newErrors.contactPhone = "Contact phone is required"
    }
    
    // Skills validation
    if (formData.skills.length === 0) {
      newErrors.skills = "At least one skill is required"
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (isSubmitting) return
    
    // Validate form before submission
    if (!validateForm()) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields correctly.",
        variant: "destructive",
      })
      return
    }
    
    setIsSubmitting(true)
    
    try {
      // Transform form data to match API format
      const createJobData: CreateJobPositionDTO = {
        title: formData.jobTitle,
        original_text: formData.jobSummary,
        summary: formData.summary,
        company: formData.company,
        city: formData.location.town,
        country: formData.location.country,
        employment_type: formData.employmentType as EmploymentType,
        seniority_level: mapExperienceLevelToSeniorityLevel(formData.experienceLevel),
        work_arrangement: mapWorkArrangement(formData.remoteWork, formData.semiRemote),
        responsibilities: formData.responsibilities ? [formData.responsibilities] : [],
        recruiter_notes: formData.recruiterNotes,
        contact_email: formData.contactInfo.email,
        contact_name: formData.contactInfo.name,
        contact_phone: formData.contactInfo.phone,
        skills: formData.skills.map(skill => ({
          name: skill.name,
          years_of_experience: skill.years,
          weight: skill.weight
        })),
        requirements: {
          certifications: formData.certifications,
          languages: formData.languages.map(lang => ({
            name: lang,
            level: "intermediate" as any // Default level
          })),
          educations: formData.educationRequirements ? [{
            field_of_study: formData.educationRequirements
          }] : []
        }
      }

      const createdJob = await jobPositionsClient.createJobPosition(createJobData)
      
      toast({
        title: "Success!",
        description: "Job position created successfully.",
      })
      
      // Navigate back to positions page or show success message
      navigate("/positions")
      
    } catch (error) {
      console.error("Error creating job position:", error)
      toast({
        title: "Error",
        description: "Failed to create job position. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleAnalyzeWithAI = async () => {
    if (!formData.jobSummary.trim()) return
    
    setIsAnalyzing(true)
    
    // Simulate AI analysis delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Here you would typically call your AI API to analyze the job summary
    // For now, we'll just move to the next step
    setCurrentStep(2)
    setIsAnalyzing(false)
  }

  return (
    <SidebarInset>
      {/* Header */}
      <motion.header
        className="flex h-16 shrink-0 items-center gap-2 border-b bg-white px-4"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" className="gap-2" onClick={() => navigate("/")}>
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
          <Separator orientation="vertical" className="h-4" />
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Create Job Position</h1>
            <div className="flex items-center gap-2 mt-1">
              <div className={`h-2 w-2 rounded-full ${currentStep >= 1 ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
              <div className={`h-2 w-2 rounded-full ${currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="mx-auto max-w-4xl p-6">
          {/* Progress Indicator */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600">
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">AI-Powered Job Creation</h2>
                  <p className="text-sm text-gray-600">Step {currentStep} of 2</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="bg-blue-50 text-blue-700">
                  AI Active
                </Badge>
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="relative w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <motion.div
                className="bg-blue-600 h-2 rounded-full"
                initial={{ width: "0%" }}
                animate={{ width: `${(currentStep / 2) * 100}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              />
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>Job Analysis</span>
              <span>Review & Edit</span>
            </div>
          </div>

          {/* Form Steps */}
          <AnimatePresence mode="wait">
            {currentStep === 1 && (
              <motion.div
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                className="space-y-6"
              >
                <Card className="border border-gray-200 shadow-md bg-white">
                  <CardHeader className="text-center pb-6">
                    <div className="flex justify-center mb-4">
                      <div className="flex items-center justify-center w-16 h-16 bg-blue-50 rounded-full">
                        <Wand2 className="h-8 w-8 text-blue-600" />
                      </div>
                    </div>
                    <CardTitle className="text-2xl font-semibold text-gray-900 mb-2">
                      Describe Your Job Position
                    </CardTitle>
                    <CardDescription className="text-gray-600 max-w-2xl mx-auto">
                      Provide a detailed description of the job position. Our AI will analyze your input and help you create a comprehensive job posting.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="px-8 pb-8">
                    <form onSubmit={handleSubmit} className="space-y-6">
                      <div className="space-y-3">
                        <Label htmlFor="job-summary" className="text-base font-medium text-gray-700">
                          Job Description Summary
                        </Label>
                        <Textarea
                          id="job-summary"
                          placeholder="Describe the position, required skills, experience level, responsibilities, and any other important details..."
                          value={formData.jobSummary}
                          onChange={(e) => updateFormData("jobSummary", e.target.value)}
                          className="min-h-[240px] resize-none text-base border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                          disabled={isAnalyzing}
                        />
                        <p className="text-sm text-gray-500">
                          Be as detailed as possible. Include skills, experience level, responsibilities, and company information.
                        </p>
                      </div>
                      
                      <div className="flex justify-center pt-4">
                        <Button 
                          type="button" 
                          onClick={handleAnalyzeWithAI}
                          disabled={!formData.jobSummary.trim() || isAnalyzing} 
                          size="lg"
                          className="min-w-[200px] bg-blue-600 hover:bg-blue-700"
                        >
                          {isAnalyzing ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Analyzing with AI...
                            </>
                          ) : (
                            <>
                              <Sparkles className="mr-2 h-4 w-4" />
                              Analyze with AI
                            </>
                          )}
                        </Button>
                      </div>
                    </form>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {currentStep === 2 && (
              <motion.div
                key="step-2"
                variants={stepVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                className="space-y-6"
              >
                <Card className="border border-gray-200 shadow-md bg-white">
                  <CardHeader className="pb-6">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="flex items-center justify-center w-10 h-10 bg-gray-100 rounded-full">
                        <Building2 className="h-5 w-5 text-gray-600" />
                      </div>
                      <div>
                        <CardTitle className="text-xl font-semibold text-gray-900">
                          Review & Edit Job Details
                        </CardTitle>
                        <CardDescription className="text-gray-600">
                          Review and edit the job details. All fields marked with * are required.
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="px-8 pb-8 space-y-8">
                                         {/* Basic Information */}
                     <div className="space-y-4">
                       <div className="flex items-center gap-3">
                         <FileText className="h-5 w-5 text-blue-600" />
                         <h3 className="text-lg font-semibold text-gray-900">Basic Information</h3>
                       </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="jobTitle" className="text-sm font-medium">Job Title *</Label>
                          <Input
                            id="jobTitle"
                            value={formData.jobTitle}
                            onChange={(e) => updateFormData("jobTitle", e.target.value)}
                            placeholder="e.g., Senior Frontend Developer"
                            className={`border-gray-200 focus:border-blue-500 focus:ring-blue-500 ${errors.jobTitle ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
                          />
                          {errors.jobTitle && (
                            <p className="text-sm text-red-600">{errors.jobTitle}</p>
                          )}
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="company" className="text-sm font-medium">Company *</Label>
                          <Input
                            id="company"
                            value={formData.company}
                            onChange={(e) => updateFormData("company", e.target.value)}
                            placeholder="e.g., TechCorp Inc."
                            className={`border-gray-200 focus:border-blue-500 focus:ring-blue-500 ${errors.company ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
                          />
                          {errors.company && (
                            <p className="text-sm text-red-600">{errors.company}</p>
                          )}
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="summary" className="text-sm font-medium">Job Summary *</Label>
                        <Textarea
                          id="summary"
                          value={formData.summary}
                          onChange={(e) => updateFormData("summary", e.target.value)}
                          placeholder="Brief description of the role..."
                          className={`min-h-[100px] border-gray-200 focus:border-blue-500 focus:ring-blue-500 ${errors.summary ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
                        />
                        {errors.summary && (
                          <p className="text-sm text-red-600">{errors.summary}</p>
                        )}
                      </div>
                    </div>

                    <Separator />

                                         {/* Location & Work Type */}
                     <div className="space-y-4">
                       <div className="flex items-center gap-3">
                         <MapPin className="h-5 w-5 text-green-600" />
                         <h3 className="text-lg font-semibold text-gray-900">Location & Work Type</h3>
                       </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="country" className="text-sm font-medium">Country *</Label>
                          <Input
                            id="country"
                            value={formData.location.country}
                            onChange={(e) => updateNestedFormData("location", "country", e.target.value)}
                            placeholder="e.g., United States"
                            className={`border-gray-200 focus:border-blue-500 focus:ring-blue-500 ${errors.country ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
                          />
                          {errors.country && (
                            <p className="text-sm text-red-600">{errors.country}</p>
                          )}
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="town" className="text-sm font-medium">Town/City *</Label>
                          <Input
                            id="town"
                            value={formData.location.town}
                            onChange={(e) => updateNestedFormData("location", "town", e.target.value)}
                            placeholder="e.g., San Francisco"
                            className={`border-gray-200 focus:border-blue-500 focus:ring-blue-500 ${errors.town ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
                          />
                          {errors.town && (
                            <p className="text-sm text-red-600">{errors.town}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-6">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="remoteWork"
                            checked={formData.remoteWork}
                            onCheckedChange={(checked) => updateFormData("remoteWork", checked)}
                          />
                          <Label htmlFor="remoteWork" className="text-sm font-medium">Remote Work</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="semiRemote"
                            checked={formData.semiRemote}
                            onCheckedChange={(checked) => updateFormData("semiRemote", checked)}
                          />
                          <Label htmlFor="semiRemote" className="text-sm font-medium">Hybrid</Label>
                        </div>
                      </div>
                    </div>

                    <Separator />

                                         {/* Employment Details */}
                     <div className="space-y-4">
                       <div className="flex items-center gap-3">
                         <Briefcase className="h-5 w-5 text-purple-600" />
                         <h3 className="text-lg font-semibold text-gray-900">Employment Details</h3>
                       </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="employmentType" className="text-sm font-medium">Employment Type *</Label>
                          <Select value={formData.employmentType} onValueChange={(value) => updateFormData("employmentType", value)}>
                            <SelectTrigger className="border-gray-200 focus:border-blue-500 focus:ring-blue-500">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="full-time">Full-time</SelectItem>
                              <SelectItem value="part-time">Part-time</SelectItem>
                              <SelectItem value="contract">Contract</SelectItem>
                              <SelectItem value="internship">Internship</SelectItem>
                              <SelectItem value="freelance">Freelance</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="experienceLevel" className="text-sm font-medium">Experience Level *</Label>
                          <Select value={formData.experienceLevel} onValueChange={(value) => updateFormData("experienceLevel", value)}>
                            <SelectTrigger className="border-gray-200 focus:border-blue-500 focus:ring-blue-500">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="junior">Junior</SelectItem>
                              <SelectItem value="mid">Mid-level</SelectItem>
                              <SelectItem value="senior">Senior</SelectItem>
                              <SelectItem value="lead">Lead</SelectItem>
                              <SelectItem value="principal">Principal</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="yearsOfExperience" className="text-sm font-medium">Years of Experience *</Label>
                          <Input
                            id="yearsOfExperience"
                            type="number"
                            min="0"
                            value={formData.yearsOfExperience}
                            onChange={(e) => updateFormData("yearsOfExperience", parseInt(e.target.value) || 0)}
                            className="border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    </div>

                    <Separator />

                                         {/* Skills */}
                     <div className="space-y-4">
                       <div className="flex items-center gap-3">
                         <Briefcase className="h-5 w-5 text-orange-600" />
                         <h3 className="text-lg font-semibold text-gray-900">Skills *</h3>
                       </div>
                       <div className="space-y-3">
                         <div className="space-y-3">
                           {formData.skills.map((skill, index) => (
                             <div key={index} className="flex items-center gap-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                               <div className="flex-1">
                                 <span className="font-medium text-gray-900">{skill.name}</span>
                               </div>
                               <div className="flex items-center gap-3">
                                 <div className="flex items-center gap-2">
                                   <Label className="text-sm font-medium text-gray-600">Years:</Label>
                                   <Input
                                     type="number"
                                     min="1"
                                     value={skill.years}
                                     onChange={(e) => {
                                       const newSkills = [...formData.skills]
                                       newSkills[index] = { ...skill, years: parseInt(e.target.value) || 1 }
                                       setFormData(prev => ({ ...prev, skills: newSkills }))
                                     }}
                                     className="w-20 h-9 border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                                   />
                                 </div>
                                 <div className="flex items-center gap-3">
                                   <Label className="text-sm font-medium text-gray-600">Weight:</Label>
                                   <div className="w-28">
                                     <Slider
                                       value={[skill.weight]}
                                       onValueChange={(value) => {
                                         const newSkills = [...formData.skills]
                                         newSkills[index] = { ...skill, weight: value[0] }
                                         setFormData(prev => ({ ...prev, skills: newSkills }))
                                       }}
                                       max={5}
                                       min={1}
                                       step={1}
                                       className="w-full"
                                     />
                                   </div>
                                   <Badge variant="secondary" className="min-w-[24px] justify-center bg-gray-100 text-gray-700 border-gray-200">
                                     {skill.weight}
                                   </Badge>
                                 </div>
                                 <Button
                                   variant="ghost"
                                   size="sm"
                                   className="h-9 w-9 p-0 hover:bg-red-50 hover:text-red-600"
                                   onClick={() => removeSkill(index)}
                                 >
                                   <X className="h-4 w-4" />
                                 </Button>
                               </div>
                             </div>
                           ))}
                          <div className="flex items-center gap-2">
                            <Input
                              placeholder="Enter skill name..."
                              value={newSkill.name}
                              onChange={(e) => setNewSkill(prev => ({ ...prev, name: e.target.value }))}
                              className="flex-1 border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                            />
                            <Button size="sm" onClick={addSkill} className="bg-blue-600 hover:bg-blue-700">
                              <Plus className="h-4 w-4" />
                            </Button>
                          </div>
                          {errors.skills && (
                            <p className="text-sm text-red-600">{errors.skills}</p>
                          )}
                         </div>
                       </div>
                     </div>

                    <Separator />

                                         {/* Languages */}
                     <div className="space-y-4">
                       <div className="flex items-center gap-3">
                         <FileText className="h-5 w-5 text-indigo-600" />
                         <h3 className="text-lg font-semibold text-gray-900">Languages</h3>
                       </div>
                      <div className="space-y-3">
                        <div className="space-y-2">
                          {formData.languages.map((language, index) => (
                            <Badge key={index} variant="outline" className="gap-2 bg-gray-50">
                              {language}
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-4 w-4 p-0 hover:bg-red-50 hover:text-red-600"
                                onClick={() => removeLanguage(index)}
                              >
                                <X className="h-3 w-3" />
                              </Button>
                            </Badge>
                          ))}
                          <div className="flex items-center gap-2">
                            <Input
                              placeholder="Language"
                              value={newLanguage}
                              onChange={(e) => setNewLanguage(e.target.value)}
                              className="w-32 border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                            />
                            <Button size="sm" onClick={addLanguage} className="bg-blue-600 hover:bg-blue-700">
                              <Plus className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <Separator />

                                         {/* Education & Certifications */}
                     <div className="space-y-4">
                       <div className="flex items-center gap-3">
                         <GraduationCap className="h-5 w-5 text-teal-600" />
                         <h3 className="text-lg font-semibold text-gray-900">Education & Certifications</h3>
                       </div>
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="educationRequirements" className="text-sm font-medium">Education Requirements</Label>
                          <Textarea
                            id="educationRequirements"
                            value={formData.educationRequirements}
                            onChange={(e) => updateFormData("educationRequirements", e.target.value)}
                            placeholder="e.g., Bachelor's degree in Computer Science or related field"
                            className="border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                          />
                        </div>
                        <div className="space-y-3">
                          <Label className="text-sm font-medium">Certifications</Label>
                          <div className="space-y-2">
                            {formData.certifications.map((cert, index) => (
                              <Badge key={index} variant="outline" className="gap-2 bg-gray-50">
                                {cert}
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-4 w-4 p-0 hover:bg-red-50 hover:text-red-600"
                                  onClick={() => removeCertification(index)}
                                >
                                  <X className="h-3 w-3" />
                                </Button>
                              </Badge>
                            ))}
                            <div className="flex items-center gap-2">
                              <Input
                                placeholder="Certification name"
                                value={newCertification}
                                onChange={(e) => setNewCertification(e.target.value)}
                                className="w-64 border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                              />
                              <Button size="sm" onClick={addCertification} className="bg-blue-600 hover:bg-blue-700">
                                <Plus className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <Separator />

                                         {/* Responsibilities & Notes */}
                     <div className="space-y-4">
                       <div className="flex items-center gap-3">
                         <FileText className="h-5 w-5 text-amber-600" />
                         <h3 className="text-lg font-semibold text-gray-900">Responsibilities & Notes</h3>
                       </div>
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="responsibilities" className="text-sm font-medium">Key Responsibilities *</Label>
                          <Textarea
                            id="responsibilities"
                            value={formData.responsibilities}
                            onChange={(e) => updateFormData("responsibilities", e.target.value)}
                            placeholder="List the main responsibilities for this role..."
                            className={`min-h-[100px] border-gray-200 focus:border-blue-500 focus:ring-blue-500 ${errors.responsibilities ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
                          />
                          {errors.responsibilities && (
                            <p className="text-sm text-red-600">{errors.responsibilities}</p>
                          )}
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="recruiterNotes" className="text-sm font-medium">Recruiter Notes</Label>
                          <Textarea
                            id="recruiterNotes"
                            value={formData.recruiterNotes}
                            onChange={(e) => updateFormData("recruiterNotes", e.target.value)}
                            placeholder="Internal notes for recruiters..."
                            className="min-h-[100px] border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    </div>

                    <Separator />

                                         {/* Contact Information */}
                     <div className="space-y-4">
                       <div className="flex items-center gap-3">
                         <User className="h-5 w-5 text-slate-600" />
                         <h3 className="text-lg font-semibold text-gray-900">Contact Information</h3>
                       </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="contactName" className="text-sm font-medium">Contact Name *</Label>
                          <Input
                            id="contactName"
                            value={formData.contactInfo.name}
                            onChange={(e) => updateNestedFormData("contactInfo", "name", e.target.value)}
                            placeholder="e.g., John Doe"
                            className={`border-gray-200 focus:border-blue-500 focus:ring-blue-500 ${errors.contactName ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
                          />
                          {errors.contactName && (
                            <p className="text-sm text-red-600">{errors.contactName}</p>
                          )}
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="contactEmail" className="text-sm font-medium">Email *</Label>
                          <Input
                            id="contactEmail"
                            type="email"
                            value={formData.contactInfo.email}
                            onChange={(e) => updateNestedFormData("contactInfo", "email", e.target.value)}
                            placeholder="e.g., john@company.com"
                            className={`border-gray-200 focus:border-blue-500 focus:ring-blue-500 ${errors.contactEmail ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
                          />
                          {errors.contactEmail && (
                            <p className="text-sm text-red-600">{errors.contactEmail}</p>
                          )}
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="contactPhone" className="text-sm font-medium">Phone *</Label>
                          <Input
                            id="contactPhone"
                            value={formData.contactInfo.phone}
                            onChange={(e) => updateNestedFormData("contactInfo", "phone", e.target.value)}
                            placeholder="e.g., +1 (555) 123-4567"
                            className={`border-gray-200 focus:border-blue-500 focus:ring-blue-500 ${errors.contactPhone ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
                          />
                          {errors.contactPhone && (
                            <p className="text-sm text-red-600">{errors.contactPhone}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8">
            <Button
              variant="outline"
              onClick={handleBack}
              disabled={currentStep === 1}
              className="gap-2 border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              <ArrowLeft className="h-4 w-4" />
              Previous
            </Button>
            <div className="flex gap-3">
              {currentStep === 1 ? (
                <Button onClick={handleNext} className="gap-2 bg-blue-600 hover:bg-blue-700">
                  Next
                  <ArrowRight className="h-4 w-4" />
                </Button>
              ) : (
                <Button 
                  onClick={handleSubmit} 
                  disabled={isSubmitting}
                  className="gap-2 bg-blue-600 hover:bg-blue-700"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating Position...
                    </>
                  ) : (
                    "Create Position"
                  )}
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
      <Toaster />
    </SidebarInset>
  )
} 