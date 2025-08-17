"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ChevronDown, ChevronUp, Download, ExternalLink, Mail, Phone, MapPin, GraduationCap, Briefcase, Brain } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import type { Candidate } from "@/lib/candidate-matching"

interface MatchedCandidatesTableProps {
  candidates: Candidate[]
}

const getMatchScoreColor = (score: number) => {
  if (score >= 90) return "bg-green-100 text-green-800 border-green-200"
  if (score >= 80) return "bg-yellow-100 text-yellow-800 border-yellow-200"
  return "bg-red-100 text-red-800 border-red-200"
}

const expandedRowVariants = {
  hidden: { 
    opacity: 0, 
    height: 0,
    scale: 0.95
  },
  visible: { 
    opacity: 1, 
    height: "auto",
    scale: 1,
    transition: {
      duration: 0.3,
      ease: "easeOut" as const
    }
  },
  exit: { 
    opacity: 0, 
    height: 0,
    scale: 0.95,
    transition: {
      duration: 0.2,
      ease: "easeIn" as const
    }
  }
}

export function MatchedCandidatesTable({ candidates }: MatchedCandidatesTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())
  const [showContacts, setShowContacts] = useState<Set<number>>(new Set())

  const toggleRow = (candidateId: number) => {
    const newExpandedRows = new Set(expandedRows)
    if (newExpandedRows.has(candidateId)) {
      newExpandedRows.delete(candidateId)
    } else {
      newExpandedRows.add(candidateId)
    }
    setExpandedRows(newExpandedRows)
  }

  const handleShowContacts = (candidateId: number) => {
    const newShowContacts = new Set(showContacts)
    newShowContacts.add(candidateId)
    setShowContacts(newShowContacts)
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Candidate</TableHead>
          <TableHead>Match Score</TableHead>
          <TableHead>Key Skills</TableHead>
          <TableHead>Location</TableHead>
          <TableHead>Experience</TableHead>
          <TableHead className="w-12"></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {candidates.map((candidate, index) => (
          <>
            <motion.tr
              key={candidate.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              className="hover:bg-muted/50 transition-colors"
            >
              <TableCell className="font-medium">{candidate.name}</TableCell>
              <TableCell>
                <Badge className={getMatchScoreColor(candidate.matchScore)}>
                  {candidate.matchScore}%
                </Badge>
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {candidate.keySkills.map((skill, skillIndex) => (
                    <Badge key={skillIndex} variant="secondary" className="text-xs">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </TableCell>
              <TableCell className="text-muted-foreground">{candidate.location}</TableCell>
              <TableCell className="text-muted-foreground">{candidate.experience}</TableCell>
              <TableCell>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleRow(candidate.id)}
                  className="h-8 w-8 p-0"
                >
                  {expandedRows.has(candidate.id) ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </TableCell>
            </motion.tr>
            
            {/* Expanded Row Details */}
            <AnimatePresence>
              {expandedRows.has(candidate.id) && (
                <motion.tr
                  key={`expanded-${candidate.id}`}
                  variants={expandedRowVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  className="bg-muted/20"
                >
                  <TableCell colSpan={6} className="p-0">
                    <motion.div 
                      className="p-6 space-y-6"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.1 }}
                    >
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* AI Matching Analysis */}
                        <Card>
                          <CardHeader className="pb-3">
                            <CardTitle className="flex items-center gap-2 text-lg">
                              <Brain className="h-5 w-5 text-blue-600" />
                              AI Matching Analysis
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-sm text-muted-foreground leading-relaxed">
                              {candidate.aiAnalysis}
                            </p>
                          </CardContent>
                        </Card>

                        {/* Candidate Information */}
                        <Card>
                          <CardHeader className="pb-3">
                            <CardTitle className="flex items-center gap-2 text-lg">
                              <GraduationCap className="h-5 w-5 text-green-600" />
                              Candidate Information
                            </CardTitle>
                          </CardHeader>
                                                     <CardContent className="space-y-3">
                             {showContacts.has(candidate.id) ? (
                               <>
                                 <div className="flex items-center gap-2">
                                   <Mail className="h-4 w-4 text-muted-foreground" />
                                   <span className="text-sm">{candidate.email}</span>
                                 </div>
                                 <div className="flex items-center gap-2">
                                   <Phone className="h-4 w-4 text-muted-foreground" />
                                   <span className="text-sm">{candidate.phone}</span>
                                 </div>
                               </>
                             ) : (
                               <Button 
                                 size="sm" 
                                 variant="outline" 
                                 onClick={() => handleShowContacts(candidate.id)}
                                 className="gap-2"
                               >
                                 <Mail className="h-4 w-4" />
                                 Show contacts
                               </Button>
                             )}
                             <div className="flex items-center gap-2">
                               <MapPin className="h-4 w-4 text-muted-foreground" />
                               <span className="text-sm">{candidate.address}</span>
                             </div>
                             <div className="flex items-center gap-2">
                               <GraduationCap className="h-4 w-4 text-muted-foreground" />
                               <span className="text-sm">{candidate.education}</span>
                             </div>
                             <Separator />
                            <div className="flex gap-2">
                              <Button size="sm" variant="outline" className="gap-2">
                                <Download className="h-4 w-4" />
                                Download CV
                              </Button>
                              <Button size="sm" variant="outline" className="gap-2" asChild>
                                <a href={candidate.linkedin} target="_blank" rel="noopener noreferrer">
                                  <ExternalLink className="h-4 w-4" />
                                  LinkedIn
                                </a>
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      </div>

                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Skills & Experience */}
                        <Card>
                          <CardHeader className="pb-3">
                            <CardTitle className="flex items-center gap-2 text-lg">
                              <Briefcase className="h-5 w-5 text-purple-600" />
                              Skills & Experience
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-3">
                              {candidate.skills.map((skill, index) => (
                                <div key={index} className="flex justify-between items-center">
                                  <span className="text-sm font-medium">{skill.name}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {skill.years} {skill.years === 1 ? 'year' : 'years'}
                                  </Badge>
                                </div>
                              ))}
                            </div>
                          </CardContent>
                        </Card>

                        {/* Work Experience */}
                        <Card>
                          <CardHeader className="pb-3">
                            <CardTitle className="flex items-center gap-2 text-lg">
                              <Briefcase className="h-5 w-5 text-orange-600" />
                              Work Experience
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              {candidate.workExperience.map((experience, index) => (
                                <div key={index} className="space-y-2">
                                  <div className="flex justify-between items-start">
                                    <div>
                                      <h4 className="font-medium text-sm">{experience.position}</h4>
                                      <p className="text-sm text-muted-foreground">{experience.company}</p>
                                    </div>
                                    <Badge variant="secondary" className="text-xs">
                                      {experience.duration}
                                    </Badge>
                                  </div>
                                  <p className="text-sm text-muted-foreground leading-relaxed">
                                    {experience.description}
                                  </p>
                                  {index < candidate.workExperience.length - 1 && (
                                    <Separator />
                                  )}
                                </div>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </motion.div>
                  </TableCell>
                </motion.tr>
              )}
            </AnimatePresence>
          </>
        ))}
      </TableBody>
    </Table>
  )
} 