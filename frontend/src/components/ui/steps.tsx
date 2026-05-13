"use client"

import { motion, AnimatePresence } from "framer-motion"

interface StepsProps {
  children: React.ReactNode[]
  currentStep: number
  onComplete?: () => void
}

export function Steps({ children, currentStep }: StepsProps) {
  return (
    <div className="w-full h-full mx-auto relative overflow-x-hidden">
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
