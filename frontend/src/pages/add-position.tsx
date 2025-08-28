"use client"

import { SidebarHeader } from "@/components/layout/sidebar-header"
import { Steps } from "@/components/ui/steps"
import { Step } from "@/components/ui/step"
import { useState } from "react"
import { Step1Chat, Step2Summary } from "@/components/add-position"
import { CreateJobPositionDTO } from "@/lib/api/types"

export function AddPositionPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const [step1Data, setStep1Data] = useState<CreateJobPositionDTO | null>(null)
  
  const handleComplete = () => {
    console.log("Position creation completed!")
    // Here you can redirect to positions list or show success message
  }

  const onStep1Complete = (data: CreateJobPositionDTO) => {
    setStep1Data(data)
    setCurrentStep(currentStep + 1)
    console.log("Step 1 completed with data:", data)
  }

  const onStep2Complete = () => {
    handleComplete()
  }

  const onStep2Back = () => {
    setCurrentStep(currentStep - 1)
  }

  return (
    <div className="flex h-screen flex-col">
      <SidebarHeader 
        title="Add Position"
        description="Create a new job position"
      />
      
      <div className="flex-1 min-h-0">
        <Steps currentStep={currentStep} onComplete={handleComplete}>
          <Step>
            <Step1Chat onComplete={onStep1Complete}/>
          </Step>
          
          <Step>
            <Step2Summary 
              onBack={onStep2Back} 
              onComplete={onStep2Complete}
              initialData={step1Data}
            />
          </Step>
        </Steps>
      </div>
    </div>
  )
}
