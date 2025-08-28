"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { ChatWindow, ChatMessage } from "./chat-window"
import { ChatInput } from "./chat-input"

interface ChatInterfaceProps {
  className?: string
  onSendMessage: (message: string) => Promise<string>
  initialMessages?: ChatMessage[]
  isLoading?: boolean
  extraButtons?: React.ReactNode
  emptyStateMessage?: {
    title: string
    description: string
    icon?: React.ReactNode
  }
}

export function ChatInterface({ className = "", onSendMessage, initialMessages = [], isLoading: externalIsLoading = false, extraButtons, emptyStateMessage }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      message,
      isAI: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Get response from onSendMessage
      const response = await onSendMessage(message)
      
      // Add AI response
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: response,
        isAI: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      
      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: "Sorry, I encountered an error. Please try again.",
        isAI: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className={`flex flex-col h-full ${className}`}
    >
      {/* Chat Window - Takes all available height */}
      <div className="flex-1 min-h-0">
        <ChatWindow 
          messages={messages} 
          isLoading={externalIsLoading || isLoading}
          className="h-full"
          emptyStateMessage={emptyStateMessage}
        />
      </div>
      
      {/* Chat Input - Fixed height at bottom */}
      <ChatInput 
        onSendMessage={handleSendMessage}
        isLoading={externalIsLoading || isLoading}
        placeholder="Type your message..."
        className="flex-shrink-0 border-t bg-background"
        extraButtons={extraButtons}
      />
    </motion.div>
  )
}
