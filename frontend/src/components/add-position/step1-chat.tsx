"use client"

import { useState } from "react"
import { ChatInterface } from "@/components/chat"
import { Button } from "@/components/ui/button"
import { CheckCircle, Sparkles } from "lucide-react"
import { AiAgentsClient } from "@/lib/api/ai-agents-client"
import { CreateJobPositionDTO } from "@/lib/api/types"
import { ModelSelector } from "@/components/model-selector"

export function Step1Chat({ onComplete }: { onComplete: (res: CreateJobPositionDTO) => void }) {
  const [messageHistory, setMessageHistory] = useState<string|undefined>(undefined)
  const [model, setModel] = useState<string|undefined>(undefined)
  const aiAgentsClient = new AiAgentsClient()

  const handleSendMessage = async (message: string): Promise<string> => {
    try {
      // Send message to AI agent with current message history
      const response = await aiAgentsClient.chatWithJobPosition({
        message: message.trim(),
        message_history: messageHistory,
        model,
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
      const res = await aiAgentsClient.analyzeJobPosition({
        message_history: messageHistory,
        model,
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
    <div className="h-full overflow-hidden flex flex-col">
      <div className="flex-1 overflow-hidden">
        <ChatInterface
          onSendMessage={handleSendMessage}
          extraButtons={completedButton}
          emptyStateMessage={emptyStateMessage}
          inputLeading={
            <ModelSelector
              value={model}
              onChange={setModel}
              purpose="chat"
              className="w-[9.5rem] sm:w-44 md:w-52 shrink-0 h-[44px]"
            />
          }
        />
      </div>
    </div>
  )
}
