"use client"

import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ArrowLeft, X, Sparkles, Loader2, Send, Bot, User, MessageCircle, Wand2, Building2, FileText, MapPin, Briefcase, GraduationCap, User as UserIcon, Mail, Phone, Plus } from "lucide-react"
import { useNavigate } from "react-router-dom"
import ReactMarkdown from 'react-markdown'
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
import { AiAgentsClient } from "@/lib/api/ai-agents-client"
import { CreateJobPositionDTO } from "@/lib/api/types"
import { EmploymentType, SeniorityLevel, WorkArrangement } from "@/lib/api/enums"
import { useToast } from "@/components/ui/use-toast"
import { Toaster } from "@/components/ui/toaster"

interface ChatMessage {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
}

interface JobSkill {
  name: string
  years: number
  weight: number
}

interface JobFormData {
  jobSummary: string
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

const messageVariants = {
  hidden: { opacity: 0, y: 10, scale: 0.95 },
  visible: { opacity: 1, y: 0, scale: 1 },
  exit: { opacity: 0, y: -10, scale: 0.95 }
}

const WELCOME_MESSAGE = "Hi! I'm here to help you create a job position, Please send me a summary of the job position"

export function AddPositionPage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<JobFormData>(initialFormData)
  const [newSkill, setNewSkill] = useState({ name: "", years: 1, weight: 3 })
  const [newLanguage, setNewLanguage] = useState("")
  const [newCertification, setNewCertification] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [showForm, setShowForm] = useState(false)
  
  // Chat interface state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'ai',
      content: `${WELCOME_MESSAGE}`,
      timestamp: new Date()
    }
  ])
  const [currentMessage, setCurrentMessage] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [messageHistory, setMessageHistory] = useState<string | undefined>(undefined)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  const { toast } = useToast()
  const jobPositionsClient = new JobPositionsClient()
  const aiAgentsClient = new AiAgentsClient()

  // Auto-scroll to bottom of chat
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight
    }
  }, [chatMessages])

  const updateFormData = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
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

  // Chat functions
  const sendMessage = async () => {
    if (!currentMessage.trim() || isTyping) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage.trim(),
      timestamp: new Date()
    }

    setChatMessages(prev => [...prev, userMessage])
    setCurrentMessage("")
    setIsTyping(true)

    try {
      // Call the real chat API
      const response = await aiAgentsClient.chatWithJobPosition({
        message: currentMessage.trim(),
        message_history: messageHistory
      })

      // Update message history for next request
      setMessageHistory(response.message_history)

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: response.output,
        timestamp: new Date()
      }

      setChatMessages(prev => [...prev, aiMessage])

      // Update job summary with accumulated conversation
      const fullConversation = [...chatMessages, userMessage, aiMessage]
        .filter(msg => msg.type === 'user')
        .map(msg => msg.content)
        .join('\n\n')
      
      updateFormData("jobSummary", fullConversation)

    } catch (error) {
      console.error("Error calling chat API:", error)
      
      // Fallback response if API fails
      const fallbackMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: "I'm sorry, I'm having trouble connecting right now. Please try again or continue with the form.",
        timestamp: new Date()
      }

      setChatMessages(prev => [...prev, fallbackMessage])
    } finally {
      setIsTyping(false)
    }
  }



  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const startOver = () => {
    setChatMessages([
      {
        id: '1',
        type: 'ai',
        content: `${WELCOME_MESSAGE}`,
        timestamp: new Date()
      }
    ])
    setCurrentMessage("")
    setMessageHistory(undefined)
    updateFormData("jobSummary", "")
    setShowForm(false)
  }

  const handleContinueToForm = () => {
    if (chatMessages.length > 1) {
      setShowForm(true)
    }
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
    
    if (formData.skills.length === 0) {
      newErrors.skills = "At least one skill is required"
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (isSubmitting) return
    
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
            level: "intermediate" as any
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

  return (
    <div className="flex h-screen flex-col">
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
            <p className="text-sm text-gray-600">Chat with AI to create your perfect job posting</p>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="w-full flex flex-col h-full">
          {!showForm ? (
            // Chat Interface
            <div className="relative h-full bg-gray-50">
              {/* Chat Messages Area - Scrollable with full height minus input */}
              <div 
                ref={messagesContainerRef}
                className="h-full overflow-y-auto p-6 space-y-6 pb-40"
              >
                {chatMessages.map((message) => (
                  <motion.div
                    key={message.id}
                    variants={messageVariants}
                    initial="hidden"
                    animate="visible"
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex items-start gap-4 max-w-[70%] ${message.type === 'user' ? 'flex-row-reverse' : ''}`}>
                      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                        message.type === 'user' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-white text-gray-600 border-2 border-gray-200 shadow-sm'
                      }`}>
                        {message.type === 'user' ? (
                          <User className="h-5 w-5" />
                        ) : (
                          <Bot className="h-5 w-5" />
                        )}
                      </div>
                      <div className={`rounded-2xl px-6 py-4 shadow-sm ${
                        message.type === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-900 border border-gray-200'
                      }`}>
                        {message.type === 'ai' ? (
                          <div className="text-base leading-relaxed prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-strong:text-gray-900 prose-code:bg-gray-100 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-sm prose-code:font-mono prose-ul:text-gray-700 prose-li:text-gray-700 prose-h1:text-xl prose-h1:font-semibold prose-h2:text-lg prose-h2:font-semibold prose-h3:text-base prose-h3:font-semibold prose-blockquote:border-l-4 prose-blockquote:border-gray-300 prose-blockquote:pl-4 prose-blockquote:italic prose-blockquote:text-gray-600 prose-ol:text-gray-700 prose-ul:list-disc prose-ol:list-decimal prose-li:my-1 prose-table:border-collapse prose-table:w-full prose-th:border prose-th:border-gray-300 prose-th:bg-gray-50 prose-th:px-3 prose-th:py-2 prose-th:text-left prose-td:border prose-td:border-gray-300 prose-td:px-3 prose-td:py-2 prose-hr:border-gray-300">
                            <ReactMarkdown>
                              {message.content}
                            </ReactMarkdown>
                          </div>
                        ) : (
                          <p className="text-base leading-relaxed whitespace-pre-wrap">{message.content}</p>
                        )}
                        <p className={`text-xs mt-3 ${
                          message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
                
                {/* Typing indicator */}
                {isTyping && (
                  <motion.div
                    variants={messageVariants}
                    initial="hidden"
                    animate="visible"
                    className="flex justify-start"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-white text-gray-600 border-2 border-gray-200 shadow-sm">
                        <Bot className="h-5 w-5" />
                      </div>
                      <div className="bg-white text-gray-900 border border-gray-200 rounded-2xl px-6 py-4 shadow-sm">
                        <div className="flex space-x-2">
                          <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
                
                <div ref={chatEndRef} />
              </div>

              {/* Chat Input Area - Fixed at Bottom */}
              <div className="absolute bottom-0 left-0 right-0 bg-white p-6 border-t border-gray-200">
                <div className="w-full space-y-4">
                  <div className="flex gap-3">
                    <Textarea
                      placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="flex-1 min-h-[60px] resize-none text-base border-gray-200 focus:border-blue-500 focus:ring-blue-500 rounded-xl"
                      disabled={isTyping}
                    />
                    <Button
                      onClick={sendMessage}
                      disabled={!currentMessage.trim() || isTyping}
                      size="lg"
                      className="px-6 h-[60px] bg-blue-600 hover:bg-blue-700 rounded-xl"
                    >
                      <Send className="h-5 w-5" />
                    </Button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-gray-500">
                      Describe the role, requirements, company culture, or any other details about the position
                    </p>
                    
                    {/* Action Buttons */}
                    <div className="flex gap-3">
                      <Button
                        variant="outline"
                        onClick={startOver}
                        className="gap-2 border-gray-300 text-gray-700 hover:bg-gray-50"
                      >
                        <X className="h-4 w-4" />
                        Start Over
                      </Button>
                      <Button 
                        onClick={handleContinueToForm}
                        disabled={chatMessages.length <= 1} 
                        size="lg"
                        className="min-w-[180px] bg-blue-600 hover:bg-blue-700"
                      >
                        <Wand2 className="mr-2 h-4 w-4" />
                        Continue to Form
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            // Form Interface
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex-1 overflow-y-auto p-6"
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
                      <UserIcon className="h-5 w-5 text-slate-600" />
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
            </motion.div>
          )}
        </div>
      </div>
      <Toaster />
    </div>
  )
} 