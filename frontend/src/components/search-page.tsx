"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ArrowLeft, ArrowRight, Plus, X, Building2, Sparkles, Loader2 } from "lucide-react"
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

interface JobSkill {
  name: string
  years: number
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
  employmentType: "fulltime" | "parttime" | "contract"
  experienceLevel: "junior" | "mid" | "senior" | "lead" | "principal"
  yearsOfExperience: number
  skills: JobSkill[]
  preferredSkills: JobSkill[]
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
  employmentType: "fulltime",
  experienceLevel: "mid",
  yearsOfExperience: 3,
  skills: [],
  preferredSkills: [],
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
  const [newSkill, setNewSkill] = useState({ name: "", years: 1 })
  const [newPreferredSkill, setNewPreferredSkill] = useState({ name: "", years: 1 })
  const [newLanguage, setNewLanguage] = useState("")
  const [newCertification, setNewCertification] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)

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
  }

  const updateNestedFormData = (parent: keyof JobFormData, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [parent]: {
        ...(prev[parent] as any),
        [field]: value
      }
    }))
  }

  const addSkill = (skillType: "skills" | "preferredSkills") => {
    const skillToAdd = skillType === "skills" ? newSkill : newPreferredSkill
    if (skillToAdd.name.trim()) {
      setFormData(prev => ({
        ...prev,
        [skillType]: [...prev[skillType], skillToAdd]
      }))
      if (skillType === "skills") {
        setNewSkill({ name: "", years: 1 })
      } else {
        setNewPreferredSkill({ name: "", years: 1 })
      }
    }
  }

  const removeSkill = (skillType: "skills" | "preferredSkills", index: number) => {
    setFormData(prev => ({
      ...prev,
      [skillType]: prev[skillType].filter((_, i) => i !== index)
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("Form submitted:", formData)
    // Here you would typically send the data to your backend
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
      <motion.header
        className="flex h-16 shrink-0 items-center gap-2 border-b px-4"
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
            <h1 className="text-lg font-semibold">Add Position</h1>
            <div className="flex items-center gap-2 mt-1">
              <div className={`h-2 w-2 rounded-full ${currentStep >= 1 ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
              <div className={`h-2 w-2 rounded-full ${currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
            </div>
          </div>
        </div>
      </motion.header>

      <div className="flex-1 overflow-auto p-6">
        <div className="mx-auto max-w-4xl">
                     {/* AI Progress Bar */}
           <div className="mb-8">
             <div className="flex items-center justify-between mb-3">
               <div className="flex items-center gap-2">
                 <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-r from-blue-500 to-indigo-600">
                   <div className="h-2 w-2 rounded-full bg-white animate-pulse"></div>
                 </div>
                 <span className="text-sm font-semibold text-gray-700">AI Processing Progress</span>
               </div>
               <div className="flex items-center gap-2">
                 <div className="flex items-center gap-1">
                   <div className={`h-2 w-2 rounded-full ${currentStep >= 1 ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
                   <div className={`h-2 w-2 rounded-full ${currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
                 </div>
                 <div className="flex items-center gap-1">
                   <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse"></div>
                   <span className="text-xs text-blue-600 font-medium">AI Active</span>
                 </div>
               </div>
             </div>
             <div className="relative w-full bg-gray-100 rounded-full h-3 overflow-hidden">
               <motion.div
                 className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full relative"
                 initial={{ width: "0%" }}
                 animate={{ width: `${(currentStep / 2) * 100}%` }}
                 transition={{ duration: 0.5, ease: "easeOut" }}
               >
                 <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
               </motion.div>
               <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-indigo-500/20 animate-pulse"></div>
             </div>
             <div className="flex justify-between mt-2 text-xs text-gray-500">
               <span>Job Analysis</span>
               <span>Review & Edit</span>
             </div>
           </div>

          <AnimatePresence mode="wait">
                         {currentStep === 1 && (
               <motion.div variants={cardVariants} initial="hidden" animate="visible">
               <Card>
                 <CardHeader className="text-center">
                   <CardTitle className="flex items-center justify-center gap-2">
                     <motion.div
                       animate={{ rotate: [0, 360] }}
                       transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                     >
                       <Sparkles className="h-5 w-5 text-primary" />
                     </motion.div>
                     AI-Powered Job Analysis
                   </CardTitle>
                   <CardDescription>
                     Describe the job position in your own words. Our AI will analyze your description and automatically fill
                     out the detailed job requirements for you to review and edit.
                   </CardDescription>
                 </CardHeader>
                 <CardContent>
                   <form onSubmit={handleSubmit} className="space-y-4">
                     <div>
                       <label htmlFor="job-summary" className="block text-sm font-medium mb-2">
                         Job Description Summary
                       </label>
                       <motion.div whileFocus={{ scale: 1.02 }} transition={{ duration: 0.2 }}>
                         <Textarea
                           id="job-summary"
                           placeholder="Describe the position, required skills, experience level, and any other important details..."
                           value={formData.jobSummary}
                           onChange={(e) => updateFormData("jobSummary", e.target.value)}
                           className="min-h-[200px] resize-none transition-all duration-200"
                           disabled={isAnalyzing}
                         />
                       </motion.div>
                       <p className="text-sm text-muted-foreground mt-2">
                         Be as detailed as possible. Include skills, experience level, responsibilities, and company
                         information.
                       </p>
                     </div>
       
                                           <div className="flex justify-center">
                        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                          <Button 
                            type="button" 
                            onClick={handleAnalyzeWithAI}
                            disabled={!formData.jobSummary.trim() || isAnalyzing} 
                            className="min-w-[200px]"
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
                        </motion.div>
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
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Building2 className="h-5 w-5" />
                      Step 2: Review & Edit
                    </CardTitle>
                    <CardDescription>
                      Review and edit the job details. All fields marked with * are required.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Basic Information */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Basic Information</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="jobTitle">Job Title *</Label>
                          <Input
                            id="jobTitle"
                            value={formData.jobTitle}
                            onChange={(e) => updateFormData("jobTitle", e.target.value)}
                            placeholder="e.g., Senior Frontend Developer"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="company">Company *</Label>
                          <Input
                            id="company"
                            value={formData.company}
                            onChange={(e) => updateFormData("company", e.target.value)}
                            placeholder="e.g., TechCorp Inc."
                          />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="summary">Job Summary *</Label>
                        <Textarea
                          id="summary"
                          value={formData.summary}
                          onChange={(e) => updateFormData("summary", e.target.value)}
                          placeholder="Brief description of the role..."
                          className="min-h-[100px]"
                        />
                      </div>
                    </div>

                    <Separator />

                    {/* Location & Work Type */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Location & Work Type</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="country">Country *</Label>
                          <Input
                            id="country"
                            value={formData.location.country}
                            onChange={(e) => updateNestedFormData("location", "country", e.target.value)}
                            placeholder="e.g., United States"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="town">Town/City *</Label>
                          <Input
                            id="town"
                            value={formData.location.town}
                            onChange={(e) => updateNestedFormData("location", "town", e.target.value)}
                            placeholder="e.g., San Francisco"
                          />
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="remoteWork"
                            checked={formData.remoteWork}
                            onCheckedChange={(checked) => updateFormData("remoteWork", checked)}
                          />
                          <Label htmlFor="remoteWork">Remote Work</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="semiRemote"
                            checked={formData.semiRemote}
                            onCheckedChange={(checked) => updateFormData("semiRemote", checked)}
                          />
                          <Label htmlFor="semiRemote">Semi-Remote</Label>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    {/* Employment Details */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Employment Details</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="employmentType">Employment Type *</Label>
                          <Select value={formData.employmentType} onValueChange={(value) => updateFormData("employmentType", value)}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="fulltime">Full-time</SelectItem>
                              <SelectItem value="parttime">Part-time</SelectItem>
                              <SelectItem value="contract">Contract</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="experienceLevel">Experience Level *</Label>
                          <Select value={formData.experienceLevel} onValueChange={(value) => updateFormData("experienceLevel", value)}>
                            <SelectTrigger>
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
                          <Label htmlFor="yearsOfExperience">Years of Experience *</Label>
                          <Input
                            id="yearsOfExperience"
                            type="number"
                            min="0"
                            value={formData.yearsOfExperience}
                            onChange={(e) => updateFormData("yearsOfExperience", parseInt(e.target.value) || 0)}
                          />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    {/* Skills & Requirements */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Skills & Requirements</h3>
                      
                      {/* Required Skills */}
                      <div className="space-y-3">
                        <Label>Required Skills</Label>
                        <div className="space-y-2">
                          {formData.skills.map((skill, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <Badge variant="secondary" className="gap-2">
                                {skill.name} ({skill.years} years)
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-4 w-4 p-0"
                                  onClick={() => removeSkill("skills", index)}
                                >
                                  <X className="h-3 w-3" />
                                </Button>
                              </Badge>
                            </div>
                          ))}
                          <div className="flex items-center gap-2">
                            <Input
                              placeholder="Skill name"
                              value={newSkill.name}
                              onChange={(e) => setNewSkill(prev => ({ ...prev, name: e.target.value }))}
                              className="w-32"
                            />
                            <Input
                              type="number"
                              min="1"
                              placeholder="Years"
                              value={newSkill.years}
                              onChange={(e) => setNewSkill(prev => ({ ...prev, years: parseInt(e.target.value) || 1 }))}
                              className="w-20"
                            />
                            <Button size="sm" onClick={() => addSkill("skills")}>
                              <Plus className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>

                      {/* Preferred Skills */}
                      <div className="space-y-3">
                        <Label>Preferred Skills</Label>
                        <div className="space-y-2">
                          {formData.preferredSkills.map((skill, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <Badge variant="outline" className="gap-2">
                                {skill.name} ({skill.years} years)
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-4 w-4 p-0"
                                  onClick={() => removeSkill("preferredSkills", index)}
                                >
                                  <X className="h-3 w-3" />
                                </Button>
                              </Badge>
                            </div>
                          ))}
                          <div className="flex items-center gap-2">
                            <Input
                              placeholder="Skill name"
                              value={newPreferredSkill.name}
                              onChange={(e) => setNewPreferredSkill(prev => ({ ...prev, name: e.target.value }))}
                              className="w-32"
                            />
                            <Input
                              type="number"
                              min="1"
                              placeholder="Years"
                              value={newPreferredSkill.years}
                              onChange={(e) => setNewPreferredSkill(prev => ({ ...prev, years: parseInt(e.target.value) || 1 }))}
                              className="w-20"
                            />
                            <Button size="sm" onClick={() => addSkill("preferredSkills")}>
                              <Plus className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>

                      {/* Languages */}
                      <div className="space-y-3">
                        <Label>Languages</Label>
                        <div className="space-y-2">
                          {formData.languages.map((language, index) => (
                            <Badge key={index} variant="outline" className="gap-2">
                              {language}
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-4 w-4 p-0"
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
                              className="w-32"
                            />
                            <Button size="sm" onClick={addLanguage}>
                              <Plus className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    {/* Education & Certifications */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Education & Certifications</h3>
                      <div className="space-y-2">
                        <Label htmlFor="educationRequirements">Education Requirements</Label>
                        <Textarea
                          id="educationRequirements"
                          value={formData.educationRequirements}
                          onChange={(e) => updateFormData("educationRequirements", e.target.value)}
                          placeholder="e.g., Bachelor's degree in Computer Science or related field"
                        />
                      </div>
                      <div className="space-y-3">
                        <Label>Certifications</Label>
                        <div className="space-y-2">
                          {formData.certifications.map((cert, index) => (
                            <Badge key={index} variant="outline" className="gap-2">
                              {cert}
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-4 w-4 p-0"
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
                              className="w-64"
                            />
                            <Button size="sm" onClick={addCertification}>
                              <Plus className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    {/* Responsibilities & Notes */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Responsibilities & Notes</h3>
                      <div className="space-y-2">
                        <Label htmlFor="responsibilities">Key Responsibilities</Label>
                        <Textarea
                          id="responsibilities"
                          value={formData.responsibilities}
                          onChange={(e) => updateFormData("responsibilities", e.target.value)}
                          placeholder="List the main responsibilities for this role..."
                          className="min-h-[100px]"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="recruiterNotes">Recruiter Notes</Label>
                        <Textarea
                          id="recruiterNotes"
                          value={formData.recruiterNotes}
                          onChange={(e) => updateFormData("recruiterNotes", e.target.value)}
                          placeholder="Internal notes for recruiters..."
                          className="min-h-[100px]"
                        />
                      </div>
                    </div>

                    <Separator />

                    {/* Contact Information */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Contact Information</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="contactName">Contact Name *</Label>
                          <Input
                            id="contactName"
                            value={formData.contactInfo.name}
                            onChange={(e) => updateNestedFormData("contactInfo", "name", e.target.value)}
                            placeholder="e.g., John Doe"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="contactEmail">Email *</Label>
                          <Input
                            id="contactEmail"
                            type="email"
                            value={formData.contactInfo.email}
                            onChange={(e) => updateNestedFormData("contactInfo", "email", e.target.value)}
                            placeholder="e.g., john@company.com"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="contactPhone">Phone</Label>
                          <Input
                            id="contactPhone"
                            value={formData.contactInfo.phone}
                            onChange={(e) => updateNestedFormData("contactInfo", "phone", e.target.value)}
                            placeholder="e.g., +1 (555) 123-4567"
                          />
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
              className="gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Previous
            </Button>
            <div className="flex gap-2">
              {currentStep === 1 ? (
                <Button onClick={handleNext} className="gap-2">
                  Next
                  <ArrowRight className="h-4 w-4" />
                </Button>
              ) : (
                <Button onClick={handleSubmit} className="gap-2">
                  Create Position
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </SidebarInset>
  )
} 