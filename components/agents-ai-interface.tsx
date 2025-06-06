"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Send,
  Shield,
  Database,
  Bot,
  User,
  Sparkles,
  Zap,
  Brain,
  Lock,
  Globe,
  MessageSquare,
  Activity,
  Eye,
  Scan,
} from "lucide-react"

interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: string
  agent?: "support" | "cybersecurity" | "general"
  metadata?: {
    source?: "local_knowledge" | "web_search" | "security_filter" | "no_data"
    sensitivity?: {
      level: string
      confidence: number
      reason: string
      can_search_web: boolean
    }
    web_sources?: Array<{
      title: string
      url: string
      snippet: string
    }>
    search_status?: string
    blocked?: boolean
  }
}

interface Agent {
  id: string
  name: string
  type: "support" | "cybersecurity" | "general"
  status: "active" | "inactive" | "busy" | "scanning"
  icon: any
  color: string
  description: string
  avatar?: string
}

export function AgentsAiInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<string>("general")
  const [securityScanActive, setSecurityScanActive] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const agents: Agent[] = [
    {
      id: "general",
      name: "Assistant IA",
      type: "general",
      status: "active",
      icon: Brain,
      color: "from-blue-600 via-purple-600 to-indigo-600",
      description: "Intelligence artificielle générale",
    },
    {
      id: "support",
      name: "Agent Support",
      type: "support",
      status: "active",
      icon: MessageSquare,
      color: "from-green-500 via-emerald-500 to-teal-600",
      description: "Support technique et assistance",
      avatar: "/images/support-avatar.png",
    },
    {
      id: "cybersecurity",
      name: "Gardien Cyber",
      type: "cybersecurity",
      status: securityScanActive ? "scanning" : "active",
      icon: Shield,
      color: "from-red-500 via-orange-500 to-yellow-500",
      description: "Protection et surveillance",
      avatar: "/images/security-robot.png",
    },
  ]

  useEffect(() => {
    // Animation du gardien cyber - scan périodique
    const interval = setInterval(() => {
      setSecurityScanActive(true)
      setTimeout(() => setSecurityScanActive(false), 3000)
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (message: string) => {
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          agent: selectedAgent,
          session_id: localStorage.getItem("session_id") || undefined,
        }),
      })

      if (!response.ok) {
        throw new Error("Erreur réseau")
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error("Erreur:", error)
      return {
        content: "Désolé, je rencontre des difficultés techniques. Veuillez réessayer dans quelques instants.",
        metadata: { source: "error" },
      }
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: "user",
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      const response = await handleSendMessage(input)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.content,
        sender: "assistant",
        timestamp: new Date().toISOString(),
        agent: selectedAgent as any,
        metadata: response.metadata,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error("Erreur:", error)
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: "Désolé, une erreur s'est produite. Veuillez réessayer.",
        sender: "assistant",
        timestamp: new Date().toISOString(),
        agent: selectedAgent as any,
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const renderAgentAvatar = (agent: Agent) => {
    if (agent.id === "cybersecurity") {
      return (
        <div className="relative">
          <div
            className={`w-16 h-16 rounded-full bg-gradient-to-r ${agent.color} flex items-center justify-center transition-all duration-500 ${
              securityScanActive ? "animate-pulse scale-110 shadow-lg shadow-red-500/50" : ""
            }`}
          >
            {agent.avatar ? (
              <img
                src={agent.avatar || "/placeholder.svg"}
                alt={agent.name}
                className={`w-12 h-12 object-cover rounded-full ${securityScanActive ? "animate-bounce" : ""}`}
              />
            ) : (
              <agent.icon className={`w-8 h-8 text-white ${securityScanActive ? "animate-spin" : ""}`} />
            )}
          </div>
          {securityScanActive && (
            <div className="absolute -top-1 -right-1">
              <div className="w-4 h-4 bg-red-500 rounded-full animate-ping"></div>
              <Scan className="absolute top-0 right-0 w-4 h-4 text-white animate-pulse" />
            </div>
          )}
          {securityScanActive && (
            <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
              <Badge variant="destructive" className="text-xs animate-pulse">
                SCAN
              </Badge>
            </div>
          )}
        </div>
      )
    }

    if (agent.id === "support" && agent.avatar) {
      return (
        <div className={`w-16 h-16 rounded-full bg-gradient-to-r ${agent.color} p-1 hover:scale-105 transition-all`}>
          <img
            src={agent.avatar || "/placeholder.svg"}
            alt={agent.name}
            className="w-full h-full object-cover rounded-full"
          />
        </div>
      )
    }

    return (
      <div
        className={`w-16 h-16 rounded-full bg-gradient-to-r ${agent.color} flex items-center justify-center hover:scale-105 transition-all`}
      >
        <agent.icon className="w-8 h-8 text-white" />
      </div>
    )
  }

  const renderMessage = (message: Message) => {
    const isUser = message.sender === "user"
    const agent = agents.find((a) => a.id === message.agent) || agents[0]

    return (
      <div
        key={message.id}
        className={`flex ${isUser ? "justify-end" : "justify-start"} mb-6 animate-in slide-in-from-bottom-2`}
      >
        <div className={`max-w-[80%] ${isUser ? "order-2" : "order-1"}`}>
          <div className="flex items-start gap-4">
            {!isUser && <div className="flex-shrink-0">{renderAgentAvatar(agent)}</div>}

            <Card
              className={`${
                isUser
                  ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0 shadow-xl"
                  : "bg-white/10 backdrop-blur-md border border-white/20 shadow-xl hover:shadow-2xl transition-all"
              }`}
            >
              <CardContent className="p-4">
                {!isUser && (
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-sm font-medium text-white/90">{agent.name}</span>
                    <div
                      className={`w-2 h-2 rounded-full ${
                        agent.status === "scanning" ? "bg-red-400 animate-pulse" : "bg-green-400"
                      }`}
                    ></div>
                  </div>
                )}

                <div className={`text-sm ${isUser ? "text-white" : "text-white/90"}`}>{message.content}</div>

                {message.metadata && !isUser && (
                  <div className="mt-3 space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      {message.metadata.source === "local_knowledge" && (
                        <Badge variant="secondary" className="text-xs bg-white/20 text-white border-white/30">
                          <Database className="w-3 h-3 mr-1" />
                          Base de connaissances
                        </Badge>
                      )}
                      {message.metadata.source === "web_search" && (
                        <Badge variant="outline" className="text-xs bg-white/20 text-white border-white/30">
                          <Globe className="w-3 h-3 mr-1" />
                          Recherche web
                        </Badge>
                      )}
                      {message.metadata.source === "security_filter" && (
                        <Badge variant="destructive" className="text-xs">
                          <Lock className="w-3 h-3 mr-1" />
                          Sécurisé
                        </Badge>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {isUser && (
              <Avatar className="w-12 h-12 flex-shrink-0">
                <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
                  <User className="w-5 h-5" />
                </AvatarFallback>
              </Avatar>
            )}
          </div>

          <div className={`text-xs text-white/60 mt-2 ${isUser ? "text-right mr-16" : "ml-20"}`}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      {/* Matrix-like code background */}
      <div className="absolute inset-0 opacity-5">
        <div className="text-green-400 text-xs font-mono leading-none select-none">
          {Array.from({ length: 50 }, (_, i) => (
            <div key={i} className="whitespace-nowrap animate-pulse" style={{ animationDelay: `${i * 0.1}s` }}>
              {Array.from({ length: 200 }, () => Math.random().toString(36).charAt(0)).join("")}
            </div>
          ))}
        </div>
      </div>

      <div className="relative z-10 flex flex-col h-screen">
        {/* Header */}
        <div className="p-6 border-b border-white/10 bg-black/20 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">NextGen AI Agents</h1>
                <p className="text-white/60">Intelligence artificielle avancée</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Activity className="w-5 h-5 text-green-400 animate-pulse" />
              <span className="text-green-400 font-medium">Système actif</span>
            </div>
          </div>
        </div>

        {/* Agent Selection */}
        <div className="p-6 bg-black/10 backdrop-blur-md border-b border-white/10">
          <div className="flex gap-6 justify-center">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className={`cursor-pointer transition-all duration-300 ${
                  selectedAgent === agent.id ? "scale-110" : "hover:scale-105"
                }`}
                onClick={() => setSelectedAgent(agent.id)}
              >
                <div className="text-center">
                  {renderAgentAvatar(agent)}
                  <div className="mt-3">
                    <h3 className="text-white font-medium text-sm">{agent.name}</h3>
                    <p className="text-white/60 text-xs mt-1">{agent.description}</p>
                    <Badge variant={agent.status === "scanning" ? "destructive" : "secondary"} className="mt-2 text-xs">
                      {agent.status === "scanning" ? "SCANNING" : agent.status.toUpperCase()}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        <ScrollArea className="flex-1 p-6">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
                <Bot className="w-12 h-12 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-white mb-4">Bienvenue dans NextGen AI</h2>
              <p className="text-white/70 mb-8 max-w-md mx-auto">
                Sélectionnez un agent spécialisé et commencez votre conversation avec l'intelligence artificielle
                avancée.
              </p>

              <div className="text-white/50 text-sm">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Eye className="w-4 h-4" />
                  <span>Surveillance continue de la sécurité</span>
                </div>
                <div className="flex items-center justify-center gap-2">
                  <Zap className="w-4 h-4" />
                  <span>Réponses instantanées et intelligentes</span>
                </div>
              </div>
            </div>
          ) : (
            messages.map(renderMessage)
          )}

          {isLoading && (
            <div className="flex justify-start mb-6 animate-in slide-in-from-bottom-2">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  {renderAgentAvatar(agents.find((a) => a.id === selectedAgent) || agents[0])}
                </div>
                <Card className="bg-white/10 backdrop-blur-md border border-white/20 shadow-xl">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                        <div
                          className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                      <span className="text-sm text-white/80">
                        {agents.find((a) => a.id === selectedAgent)?.name} analyse...
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </ScrollArea>

        {/* Input Area */}
        <div className="p-6 bg-black/20 backdrop-blur-md border-t border-white/10">
          <div className="flex gap-4 items-end max-w-4xl mx-auto">
            <div className="flex-1">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={`Parlez avec ${agents.find((a) => a.id === selectedAgent)?.name}...`}
                onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                disabled={isLoading}
                className="min-h-[60px] text-base bg-white/10 border-white/20 text-white placeholder-white/50 focus:border-blue-400 rounded-2xl px-6 py-4 backdrop-blur-md"
              />
            </div>
            <Button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              size="lg"
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white border-0 rounded-2xl px-8 py-4 shadow-xl hover:shadow-2xl transition-all h-[60px]"
            >
              {isLoading ? <Zap className="w-6 h-6 animate-spin" /> : <Send className="w-6 h-6" />}
            </Button>
          </div>

          <div className="text-xs text-white/40 mt-4 text-center flex items-center justify-center gap-2">
            <Sparkles className="w-3 h-3" />
            NextGen AI - Sécurisé par l'intelligence artificielle avancée
            <Sparkles className="w-3 h-3" />
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  )
}
