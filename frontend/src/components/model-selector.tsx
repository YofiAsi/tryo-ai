"use client"

import { useEffect } from "react"
import useSWR from "swr"
import { llmClient } from "@/lib/api"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface ModelSelectorProps {
  value: string | undefined
  onChange: (model: string) => void
  purpose?: "chat" | "analyzer"
  className?: string
}

export function ModelSelector({
  value,
  onChange,
  purpose = "chat",
  className,
}: ModelSelectorProps) {
  const { data, error, isLoading } = useSWR("llm:models", () => llmClient.listModels(), {
    revalidateOnFocus: false,
  })

  useEffect(() => {
    if (value || !data) return
    const fallback = purpose === "analyzer" ? data.default_analyzer : data.default_chat
    if (fallback) onChange(fallback)
  }, [data, value, purpose, onChange])

  if (isLoading || !data) {
    return (
      <Select disabled>
        <SelectTrigger className={className}>
          <SelectValue placeholder="Loading models…" />
        </SelectTrigger>
      </Select>
    )
  }

  if (error) {
    return (
      <Select disabled>
        <SelectTrigger className={className}>
          <SelectValue placeholder="Models unavailable" />
        </SelectTrigger>
      </Select>
    )
  }

  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className={className}>
        <SelectValue placeholder="Select a model" />
      </SelectTrigger>
      <SelectContent>
        {data.models.map((m) => (
          <SelectItem key={m.id} value={m.id}>
            {m.id}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
