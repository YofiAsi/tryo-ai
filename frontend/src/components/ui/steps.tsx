"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface StepsProps {
  children: React.ReactNode[]
  currentStep: number
  onComplete?: () => void
}

export function Steps({ children, currentStep, onComplete }: StepsProps) {
  const totalSteps = children.length

  return (
    <div className="w-full h-full mx-auto relative overflow-x-hidden">
      {/* Floating step indicator */}
      <TooltipProvider delayDuration={300}>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="absolute top-4 right-4 flex items-center gap-2 p-2 bg-background border rounded-lg shadow-sm z-50 cursor-pointer hover:bg-muted/50 transition-colors">
              {Array.from({ length: totalSteps }).map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    index === currentStep
                      ? "bg-primary"
                      : "bg-muted-foreground"
                  }`}
                />
              ))}
            </div>
          </TooltipTrigger>
          <TooltipContent side="left" className="z-[60]">
            <p>Step {currentStep + 1} of {totalSteps}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="h-full w-full"
          >
            {children[currentStep]}
          </motion.div>
        </AnimatePresence>
    </div>
  )
}
