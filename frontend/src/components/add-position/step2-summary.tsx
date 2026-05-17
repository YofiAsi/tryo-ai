"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  FileText, 
  MapPin, 
  Briefcase, 
  GraduationCap, 
  UserIcon, 
  X, 
  Plus, 
  Loader2, 
  Sparkles,
  ArrowLeft,
  CheckCircle
} from "lucide-react"
import { JobPositionFormData, FormErrors } from "@/types/position"
import { CreateJobPositionDTO, JobSkill } from "@/lib/api/types"
import { WorkArrangement, EmploymentType, SeniorityLevel } from "@/lib/api/enums"
import { JobPositionsClient } from "@/lib/api/job-positions-client"

interface Step2SummaryProps {
  onComplete?: () => void
  onBack?: () => void
  initialData?: CreateJobPositionDTO | null
}

export function Step2Summary({ onComplete, onBack, initialData }: Step2SummaryProps) {
  const [formData, setFormData] = useState<JobPositionFormData>(() => {
    if (initialData) {
      // Map CreateJobPositionDTO to JobPositionFormData
      return {
        jobTitle: initialData.title || "",
        company: initialData.company || "",
        summary: initialData.summary || "",
        location: {
          country: initialData.country || "",
          town: initialData.city || ""
        },
        remoteWork: initialData.work_arrangement === "remote",
        semiRemote: initialData.work_arrangement === "hybrid",
        employmentType: initialData.employment_type || "",
        experienceLevel: initialData.seniority_level || "",
        yearsOfExperience: 0, // Not provided in initial data
        skills: initialData.skills?.map((skill: JobSkill) => ({
          name: skill.name || "",
          years: skill.years_of_experience || 1,
          weight: skill.weight || 3
        })) || [],
        languages: [], // Not provided in initial data
        educationRequirements: "", // Not provided in initial data
        certifications: [], // Not provided in initial data
        responsibilities: initialData.responsibilities?.join("\n") || "",
        recruiterNotes: initialData.recruiter_notes || "",
        contactInfo: {
          name: initialData.contact_name || "",
          email: initialData.contact_email || "",
          phone: initialData.contact_phone || ""
        }
      }
    }
    
    // Default empty form
    return {
      jobTitle: "",
      company: "",
      summary: "",
      location: {
        country: "",
        town: ""
      },
      remoteWork: false,
      semiRemote: false,
      employmentType: "",
      experienceLevel: "",
      yearsOfExperience: 0,
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
  })

  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [newSkill, setNewSkill] = useState({ name: "", years: 1, weight: 3 })
  const [newLanguage, setNewLanguage] = useState("")
  const [newCertification, setNewCertification] = useState("")
  const jobPositionsClient = new JobPositionsClient()

  const updateFormData = (field: keyof JobPositionFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  const updateNestedFormData = (parentField: keyof JobPositionFormData, childField: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [parentField]: {
        ...prev[parentField] as any,
        [childField]: value
      }
    }))
    // Clear error when user starts typing
    if (errors[childField as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [childField]: undefined }))
    }
  }

  const addSkill = () => {
    if (newSkill.name.trim()) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, { ...newSkill, name: newSkill.name.trim() }]
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
    if (newLanguage.trim() && !formData.languages.includes(newLanguage.trim())) {
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
    if (newCertification.trim() && !formData.certifications.includes(newCertification.trim())) {
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

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!formData.jobTitle.trim()) {
      newErrors.jobTitle = "Job title is required"
    }
    if (!formData.company.trim()) {
      newErrors.company = "Company is required"
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
    if (formData.skills.length === 0) {
      newErrors.skills = "At least one skill is required"
    }
    if (!formData.responsibilities.trim()) {
      newErrors.responsibilities = "Key responsibilities are required"
    }
    if (!formData.contactInfo.name.trim()) {
      newErrors.contactName = "Contact name is required"
    }
    if (!formData.contactInfo.email.trim()) {
      newErrors.contactEmail = "Email is required"
    }
    if (!formData.contactInfo.phone.trim()) {
      newErrors.contactPhone = "Phone is required"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    
    try {
      // Map form data to CreateJobPositionDTO
      const createJobPositionData: CreateJobPositionDTO = {
        title: formData.jobTitle,
        original_text: initialData?.original_text || "", // Use from Step1 if available
        summary: formData.summary,
        company: formData.company,
        city: formData.location.town,
        country: formData.location.country,
        employment_type: formData.employmentType as EmploymentType,
        seniority_level: formData.experienceLevel as SeniorityLevel,
        work_arrangement: formData.remoteWork ? WorkArrangement.REMOTE : formData.semiRemote ? WorkArrangement.HYBRID : WorkArrangement.ON_SITE,
        responsibilities: formData.responsibilities ? formData.responsibilities.split('\n').filter(line => line.trim()) : [],
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
          languages: formData.languages.map(lang => ({ name: lang, level: "intermediate" as any })),
          educations: formData.educationRequirements ? [{ field_of_study: formData.educationRequirements }] : []
        }
      }

      // Create job position using the API client
      const createdJobPosition = await jobPositionsClient.createJobPosition(createJobPositionData)
      
      console.log("Job position created successfully:", createdJobPosition)
      
      if (onComplete) {
        onComplete()
      }
    } catch (error) {
      console.error("Error creating job position:", error)
      // You could add error handling here, like showing a toast notification
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Create Job Position</h1>
            <p className="text-muted-foreground mt-2">Fill in the details for your new job position</p>
          </div>
          {onBack && (
            <Button variant="outline" onClick={onBack} className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
          )}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Step 2: Position Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Basic Information */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-foreground">Basic Information</h3>
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
                <h3 className="text-lg font-semibold text-foreground">Location & Work Type</h3>
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
                <h3 className="text-lg font-semibold text-foreground">Employment Details</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="employmentType" className="text-sm font-medium">Employment Type *</Label>
                  <Select value={formData.employmentType} onValueChange={(value) => updateFormData("employmentType", value)}>
                    <SelectTrigger className="border-gray-200 focus:border-blue-500 focus:ring-blue-500">
                      <SelectValue placeholder="Select type" />
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
                      <SelectValue placeholder="Select level" />
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
                <h3 className="text-lg font-semibold text-foreground">Skills *</h3>
              </div>
              <div className="space-y-3">
                <div className="space-y-3">
                  {formData.skills.map((skill, index) => (
                    <div key={index} className="flex items-center gap-4 p-4 bg-muted/50 border border-border rounded-lg">
                      <div className="flex-1">
                        <span className="font-medium text-foreground">{skill.name}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                          <Label className="text-sm font-medium text-muted-foreground">Years:</Label>
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
                          <Label className="text-sm font-medium text-muted-foreground">Weight:</Label>
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
                          <Badge variant="secondary" className="min-w-[24px] justify-center bg-muted text-muted-foreground border-border">
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
                <h3 className="text-lg font-semibold text-foreground">Languages</h3>
              </div>
              <div className="space-y-3">
                <div className="space-y-2">
                  {formData.languages.map((language, index) => (
                    <Badge key={index} variant="outline" className="gap-2 bg-muted/50">
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
                <h3 className="text-lg font-semibold text-foreground">Education & Certifications</h3>
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
                      <Badge key={index} variant="outline" className="gap-2 bg-muted/50">
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
                <h3 className="text-lg font-semibold text-foreground">Responsibilities & Notes</h3>
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
                <UserIcon className="h-5 w-5 text-muted-foreground" />
                <h3 className="text-lg font-semibold text-foreground">Contact Information</h3>
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

            {/* Submit Button */}
            <div className="flex justify-end pt-6">
              <Button
                onClick={handleSubmit}
                disabled={isSubmitting}
                size="lg"
                className="min-w-[180px] bg-blue-600 hover:bg-blue-700"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Create Job Position
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
