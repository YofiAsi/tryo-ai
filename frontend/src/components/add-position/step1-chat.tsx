"use client"

import { useState } from "react"
import { ChatInterface } from "@/components/chat"
import { Button } from "@/components/ui/button"
import { CheckCircle, Sparkles } from "lucide-react"
import { AiAgentsClient } from "@/lib/api/ai-agents-client"
import { CreateJobPositionDTO } from "@/lib/api/types"

export function Step1Chat({ onComplete }: { onComplete: (res: CreateJobPositionDTO) => void }) {
  const [messageHistory, setMessageHistory] = useState<string|undefined>(undefined)
  const aiAgentsClient = new AiAgentsClient()

  const handleSendMessage = async (message: string): Promise<string> => {
    try {
      // Send message to AI agent with current message history
      const response = await aiAgentsClient.chatWithJobPosition({
        message: message.trim(),
        message_history: messageHistory
      })
      
      // Update message history with the response
      if (response.message_history) {
        setMessageHistory(response.message_history)
      }
      
      // Return the AI response
      return response.output
    } catch (error) {
      console.error('Error chatting with AI agent:', error)
      return "Sorry, I encountered an error. Please try again."
    }
  }

  const handleComplete = async () => {
    console.log('Step 1 completed!')
    if (messageHistory) {
      let res = await aiAgentsClient.analyzeJobPosition({
        message_history: messageHistory
      })
      onComplete(res);
    }
  }

  const completedButton = (
    <Button
      onClick={handleComplete}
      size="icon"
      className="h-[44px] w-[44px] shrink-0 bg-blue-500 hover:bg-blue-600"
    >
      <CheckCircle className="w-4 h-4 text-white" />
    </Button>
  )

  const emptyStateMessage = {
    title: "Let's start!",
    description: "Send me a summary of the job description and we'll begin",
    icon: <Sparkles className="w-8 h-8" />
  }

  return (
    <div className="h-full overflow-hidden">
      <ChatInterface 
        onSendMessage={handleSendMessage}
        extraButtons={completedButton}
        emptyStateMessage={emptyStateMessage}
      />
    </div>
  )
}
