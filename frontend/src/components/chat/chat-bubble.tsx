"use client"

import { motion } from "framer-motion"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Bot, User } from "lucide-react"
import ReactMarkdown from "react-markdown"

interface ChatBubbleProps {
  message: string
  isAI: boolean
  className?: string
}

export function ChatBubble({ message, isAI, className = "" }: ChatBubbleProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isAI ? 'justify-start' : 'justify-end'} ${className}`}
    >
      {isAI && (
        <Avatar className="w-8 h-8">
          <AvatarImage src="/ai-avatar.png" alt="AI Assistant" />
          <AvatarFallback className="bg-primary text-primary-foreground">
            <Bot className="w-4 h-4" />
          </AvatarFallback>
        </Avatar>
      )}
      
      <div className={`flex flex-col max-w-[80%] ${isAI ? 'items-start' : 'items-end'}`}>
        <div
          className={`px-4 py-3 rounded-2xl ${
            isAI
              ? 'bg-muted text-foreground rounded-tl-sm'
              : 'bg-primary text-primary-foreground rounded-tr-sm'
          }`}
        >
          <div
            className={`text-sm leading-relaxed prose prose-sm max-w-none ${
              isAI ? 'text-foreground dark:prose-invert' : 'text-primary-foreground'
            }`}
          >
            <ReactMarkdown>{message}</ReactMarkdown>
          </div>
        </div>
      </div>
      
      {!isAI && (
        <Avatar className="w-8 h-8">
          <AvatarImage src="/user-avatar.png" alt="User" />
          <AvatarFallback className="bg-secondary text-secondary-foreground">
            <User className="w-4 h-4" />
          </AvatarFallback>
        </Avatar>
      )}
    </motion.div>
  )
}
