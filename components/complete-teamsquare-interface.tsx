"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Send, Bot, User, Brain, Database, Clock, MessageSquare, TrendingUp, Shield, Network } from "lucide-react"
import NetworkXStatsPanel from "@/components/networkx-stats-panel"

interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: Date
  metadata?: {
    confidence?: number
    sources_count?: number
    graph_hits?: number
    response_time?: number
    provider?: string
    memory_context_used?: boolean
  }
}

interface SystemStats {
  total_queries: number
  vector_hits: number
  graph_hits: number
  memory_hits: number
  avg_confidence: number
  avg_response_time: number
  memory_sessions: number
}

export default function CompleteTeamSquareInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content:
        "Bonjour ! Je suis l'assistant TeamSquare hybride avec RAG vectoriel, NetworkX Graph, mémoire conversationnelle et LLM intelligent. Je peux vous aider avec toutes vos questions sur TeamSquare !",
      sender: "assistant",
      timestamp: new Date(),
      metadata: {
        confidence: 1.0,
        sources_count: 0,
        graph_hits: 0,
        response_time: 0,
        provider: "system",
        memory_context_used: false,
      },
    },
  ])

  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(`session_${Date.now()}`)
  const [systemStats, setSystemStats] = useState<SystemStats>({
    total_queries: 0,
    vector_hits: 0,
    graph_hits: 0,
    memory_hits: 0,
    avg_confidence: 0,
    avg_response_time: 0,
    memory_sessions: 1,
  })

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      const response = await fetch("/api/agentic-networkx", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: inputValue,
          session_id: sessionId,
        }),
      })

      if (!response.ok) {
        throw new Error("Erreur réseau")
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.content || data.response || "Désolé, je n'ai pas pu traiter votre demande.",
        sender: "assistant",
        timestamp: new Date(),
        metadata: {
          confidence: data.metadata?.confidence || data.confidence || 0,
          sources_count: data.metadata?.sources_count || data.sources_count || 0,
          graph_hits: data.metadata?.graph_hits || data.graph_hits || 0,
          response_time: data.metadata?.response_time || data.response_time || 0,
          provider: data.metadata?.provider || data.provider || "unknown",
          memory_context_used: data.metadata?.memory_context_used || data.memory_context_used || false,
        },
      }

      setMessages((prev) => [...prev, assistantMessage])

      // Mettre à jour les statistiques
      setSystemStats((prev) => ({
        total_queries: prev.total_queries + 1,
        vector_hits: prev.vector_hits + (assistantMessage.metadata?.sources_count || 0 > 0 ? 1 : 0),
        graph_hits: prev.graph_hits + (assistantMessage.metadata?.graph_hits || 0 > 0 ? 1 : 0),
        memory_hits: prev.memory_hits + (assistantMessage.metadata?.memory_context_used ? 1 : 0),
        avg_confidence:
          (prev.avg_confidence * prev.total_queries + (assistantMessage.metadata?.confidence || 0)) /
          (prev.total_queries + 1),
        avg_response_time:
          (prev.avg_response_time * prev.total_queries + (assistantMessage.metadata?.response_time || 0)) /
          (prev.total_queries + 1),
        memory_sessions: prev.memory_sessions,
      }))
    } catch (error) {
      console.error("Erreur:", error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Désolé, une erreur s'est produite. Veuillez réessayer.",
        sender: "assistant",
        timestamp: new Date(),
        metadata: {
          confidence: 0,
          sources_count: 0,
          graph_hits: 0,
          response_time: 0,
          provider: "error",
          memory_context_used: false,
        },
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return "text-green-600"
    if (confidence >= 0.4) return "text-yellow-600"
    return "text-red-600"
  }

  const getConfidenceBadgeVariant = (confidence: number) => {
    if (confidence >= 0.7) return "default"
    if (confidence >= 0.4) return "secondary"
    return "destructive"
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Panneau de statistiques */}
        <div className="lg:col-span-1 space-y-4">
          <NetworkXStatsPanel />

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Shield className="h-5 w-5 text-green-600" />
                Fonctionnalités
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">RAG Vectoriel (ChromaDB)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">RAG Graphique (NetworkX)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Mémoire Conversationnelle</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">LLM Hybride (Gemini/Mistral)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Base TeamSquare</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Interface de chat principale */}
        <div className="lg:col-span-3">
          <Card className="h-[80vh] flex flex-col">
            <CardHeader className="border-b">
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-6 w-6 text-blue-600" />
                Assistant TeamSquare Hybride
                <Badge variant="outline" className="ml-auto">
                  Session: {sessionId.slice(-6)}
                </Badge>
              </CardTitle>
              <CardDescription>
                RAG Vectoriel + NetworkX Graph + Mémoire Conversationnelle + LLM Intelligent
              </CardDescription>
            </CardHeader>

            <CardContent className="flex-1 flex flex-col p-0">
              <ScrollArea className="flex-1 p-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                    >
                      {message.sender === "assistant" && (
                        <Avatar className="h-8 w-8 mt-1">
                          <AvatarFallback className="bg-blue-100 text-blue-600">
                            <Bot className="h-4 w-4" />
                          </AvatarFallback>
                        </Avatar>
                      )}

                      <div className={`max-w-[80%] ${message.sender === "user" ? "order-2" : ""}`}>
                        <div
                          className={`rounded-lg p-3 ${
                            message.sender === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        </div>

                        {message.metadata && message.sender === "assistant" && (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {message.metadata.confidence !== undefined && (
                              <Badge
                                variant={getConfidenceBadgeVariant(message.metadata.confidence)}
                                className="text-xs"
                              >
                                <TrendingUp className="h-3 w-3 mr-1" />
                                {(message.metadata.confidence * 100).toFixed(0)}%
                              </Badge>
                            )}

                            {message.metadata.sources_count !== undefined && message.metadata.sources_count > 0 && (
                              <Badge variant="outline" className="text-xs">
                                <Database className="h-3 w-3 mr-1" />
                                {message.metadata.sources_count} sources
                              </Badge>
                            )}

                            {message.metadata.graph_hits !== undefined && message.metadata.graph_hits > 0 && (
                              <Badge variant="secondary" className="text-xs">
                                <Network className="h-3 w-3 mr-1" />
                                {message.metadata.graph_hits} graph
                              </Badge>
                            )}

                            {message.metadata.memory_context_used && (
                              <Badge variant="secondary" className="text-xs">
                                <Brain className="h-3 w-3 mr-1" />
                                Mémoire
                              </Badge>
                            )}

                            {message.metadata.response_time !== undefined && (
                              <Badge variant="outline" className="text-xs">
                                <Clock className="h-3 w-3 mr-1" />
                                {message.metadata.response_time.toFixed(1)}s
                              </Badge>
                            )}

                            {message.metadata.provider && (
                              <Badge variant="outline" className="text-xs">
                                {message.metadata.provider}
                              </Badge>
                            )}
                          </div>
                        )}

                        <p className="text-xs text-gray-500 mt-1">{message.timestamp.toLocaleTimeString()}</p>
                      </div>

                      {message.sender === "user" && (
                        <Avatar className="h-8 w-8 mt-1 order-1">
                          <AvatarFallback className="bg-blue-600 text-white">
                            <User className="h-4 w-4" />
                          </AvatarFallback>
                        </Avatar>
                      )}
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex gap-3 justify-start">
                      <Avatar className="h-8 w-8 mt-1">
                        <AvatarFallback className="bg-blue-100 text-blue-600">
                          <Bot className="h-4 w-4" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="bg-gray-100 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                          <span className="text-sm text-gray-600">L'assistant réfléchit...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div ref={messagesEndRef} />
              </ScrollArea>

              <div className="border-t p-4">
                <div className="flex gap-2">
                  <Input
                    ref={inputRef}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Posez votre question sur TeamSquare..."
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button onClick={sendMessage} disabled={isLoading || !inputValue.trim()} size="icon">
                    <Send className="h-4 w-4" />
                  </Button>
                </div>

                <div className="mt-2 text-xs text-gray-500 flex items-center gap-4">
                  <span className="flex items-center gap-1">
                    <MessageSquare className="h-3 w-3" />
                    {messages.length - 1} messages
                  </span>
                  <span className="flex items-center gap-1">
                    <Database className="h-3 w-3" />
                    10 documents
                  </span>
                  <span className="flex items-center gap-1">
                    <Network className="h-3 w-3" />
                    {systemStats.graph_hits} graph hits
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
