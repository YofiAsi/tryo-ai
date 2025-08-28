"use client"

import { motion } from "framer-motion"

interface StepProps {
  children: React.ReactNode
}

export function Step({ children }: StepProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="h-full w-full"
    >
      {children}
    </motion.div>
  )
}
