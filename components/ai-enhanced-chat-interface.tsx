"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ThemeToggle } from "@/components/theme-toggle"
import {
  Send,
  Shield,
  Database,
  User,
  Sparkles,
  Zap,
  Brain,
  Lock,
  Globe,
  MessageSquare,
  Activity,
  Atom,
  CircuitBoard,
  Radar,
  Wand2,
  Stars,
  Orbit,
  Hexagon,
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
  status: "active" | "inactive" | "busy"
  icon: any
  color: string
  description: string
  aiIcon: any
}

export function AIEnhancedChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<string>("general")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const agents: Agent[] = [
    {
      id: "general",
      name: "Assistant Général",
      type: "general",
      status: "active",
      icon: Brain,
      aiIcon: Atom,
      color: "from-purple-500 via-violet-500 to-indigo-500",
      description: "Intelligence artificielle polyvalente avec capacités avancées",
    },
    {
      id: "support",
      name: "Agent Support",
      type: "support",
      status: "active",
      icon: MessageSquare,
      aiIcon: CircuitBoard,
      color: "from-emerald-500 via-teal-500 to-cyan-500",
      description: "Support technique intelligent et résolution de problèmes",
    },
    {
      id: "cybersecurity",
      name: "Agent Cybersécurité",
      type: "cybersecurity",
      status: "active",
      icon: Shield,
      aiIcon: Radar,
      color: "from-red-500 via-pink-500 to-rose-500",
      description: "Analyse de sécurité avancée et détection de menaces",
    },
  ]

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

  const renderMessage = (message: Message) => {
    const isUser = message.sender === "user"
    const agent = agents.find((a) => a.id === message.agent) || agents[0]

    return (
      <div
        key={message.id}
        className={`flex ${isUser ? "justify-end" : "justify-start"} mb-6 animate-in slide-in-from-bottom-2`}
      >
        <div className={`max-w-[80%] ${isUser ? "order-2" : "order-1"}`}>
          <div className="flex items-start gap-3">
            {!isUser && (
              <Avatar className="w-12 h-12 ring-2 ring-purple-500/20">
                <div
                  className={`w-full h-full bg-gradient-to-br ${agent.color} flex items-center justify-center rounded-full relative overflow-hidden`}
                >
                  <agent.aiIcon className="w-6 h-6 text-white z-10" />
                  <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent" />
                  <div className="absolute inset-0 animate-pulse bg-white/10" />
                </div>
              </Avatar>
            )}

            <Card
              className={`${
                isUser
                  ? "bg-gradient-to-br from-purple-500 via-violet-500 to-indigo-500 text-white border-0 shadow-xl glow-animation"
                  : "bg-card/80 backdrop-blur-sm border border-purple-200/50 shadow-lg hover:shadow-xl transition-all duration-300 dark:border-purple-800/50"
              }`}
            >
              <CardContent className="p-4">
                {!isUser && (
                  <div className="flex items-center gap-2 mb-3">
                    <div className="flex items-center gap-2">
                      <agent.aiIcon className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                      <span className="text-sm font-medium text-purple-700 dark:text-purple-300">{agent.name}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                      <Sparkles className="w-3 h-3 text-purple-500 animate-pulse" />
                    </div>
                  </div>
                )}

                <div className={`text-sm leading-relaxed ${isUser ? "text-white" : "text-foreground"}`}>
                  {message.content}
                </div>

                {/* Métadonnées avec style amélioré */}
                {message.metadata && !isUser && (
                  <div className="mt-4 space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      {message.metadata.source === "local_knowledge" && (
                        <Badge
                          variant="secondary"
                          className="text-xs bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300"
                        >
                          <Database className="w-3 h-3 mr-1" />
                          Base de connaissances
                        </Badge>
                      )}
                      {message.metadata.source === "web_search" && (
                        <Badge
                          variant="outline"
                          className="text-xs border-emerald-200 text-emerald-700 dark:border-emerald-800 dark:text-emerald-300"
                        >
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
              <Avatar className="w-12 h-12 ring-2 ring-purple-500/20">
                <AvatarFallback className="bg-gradient-to-br from-purple-500 to-indigo-500 text-white">
                  <User className="w-6 h-6" />
                </AvatarFallback>
              </Avatar>
            )}
          </div>

          <div className={`text-xs text-muted-foreground mt-2 ${isUser ? "text-right mr-15" : "ml-15"}`}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-background via-purple-50/30 to-indigo-50/30 dark:from-background dark:via-purple-950/20 dark:to-indigo-950/20">
      {/* En-tête ultra moderne */}
      <CardHeader className="border-b bg-card/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 via-violet-500 to-indigo-500 rounded-2xl flex items-center justify-center float-animation">
                <Orbit className="w-6 h-6 text-white" />
                <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent rounded-2xl" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 bg-clip-text text-transparent">
                NextGen AI Assistant
              </h1>
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <Stars className="w-4 h-4 text-purple-500" />
                Intelligence artificielle de nouvelle génération
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/30">
              <Activity className="w-4 h-4 text-green-500 animate-pulse" />
              <span className="text-sm text-green-600 dark:text-green-400 font-medium">En ligne</span>
            </div>
            <ThemeToggle />
          </div>
        </CardTitle>
      </CardHeader>

      {/* Sélection d'agents avec design amélioré */}
      <div className="p-6 bg-card/50 backdrop-blur-sm border-b border-purple-200/50 dark:border-purple-800/50">
        <div className="flex gap-4 overflow-x-auto">
          {agents.map((agent) => (
            <Button
              key={agent.id}
              variant={selectedAgent === agent.id ? "default" : "outline"}
              size="lg"
              onClick={() => setSelectedAgent(agent.id)}
              className={`flex items-center gap-3 whitespace-nowrap transition-all duration-300 min-w-fit px-6 py-3 ${
                selectedAgent === agent.id
                  ? `bg-gradient-to-r ${agent.color} text-white border-0 shadow-lg hover:shadow-xl pulse-glow`
                  : "hover:shadow-md hover:border-purple-300 dark:hover:border-purple-700"
              }`}
            >
              <div className="relative">
                <agent.aiIcon className="w-5 h-5" />
                {selectedAgent === agent.id && (
                  <div className="absolute inset-0 animate-ping">
                    <agent.aiIcon className="w-5 h-5 opacity-75" />
                  </div>
                )}
              </div>
              <span className="font-medium">{agent.name}</span>
              <div
                className={`w-2 h-2 rounded-full ${agent.status === "active" ? "bg-green-400 animate-pulse" : "bg-gray-400"}`}
              />
            </Button>
          ))}
        </div>
      </div>

      {/* Zone de messages */}
      <ScrollArea className="flex-1 p-6">
        {messages.length === 0 ? (
          <div className="text-center py-16">
            <div className="relative mb-8">
              <div className="w-24 h-24 bg-gradient-to-br from-purple-500 via-violet-500 to-indigo-500 rounded-3xl flex items-center justify-center mx-auto float-animation">
                <Hexagon className="w-12 h-12 text-white" />
                <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent rounded-3xl" />
              </div>
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-32 h-32 bg-purple-500/20 rounded-full blur-xl animate-pulse" />
            </div>

            <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 bg-clip-text text-transparent mb-4">
              Bonjour ! Je suis votre assistant IA
            </h2>
            <p className="text-muted-foreground mb-12 max-w-md mx-auto text-lg">
              Choisissez un agent spécialisé et découvrez les capacités de l'intelligence artificielle avancée
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              {agents.map((agent, index) => (
                <Card
                  key={agent.id}
                  className="hover:shadow-xl transition-all duration-300 cursor-pointer group border-purple-200/50 dark:border-purple-800/50 hover:border-purple-300 dark:hover:border-purple-700"
                  onClick={() => setSelectedAgent(agent.id)}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <CardContent className="p-8 text-center">
                    <div className="relative mb-6">
                      <div
                        className={`w-16 h-16 bg-gradient-to-br ${agent.color} rounded-2xl flex items-center justify-center mx-auto group-hover:scale-110 transition-transform duration-300`}
                      >
                        <agent.aiIcon className="w-8 h-8 text-white" />
                        <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent rounded-2xl" />
                      </div>
                      <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-20 h-20 bg-purple-500/10 rounded-full blur-xl group-hover:bg-purple-500/20 transition-colors duration-300" />
                    </div>
                    <h3 className="font-bold text-lg text-foreground mb-3">{agent.name}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{agent.description}</p>
                    <div className="mt-4 flex items-center justify-center gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                      <span className="text-xs text-green-600 dark:text-green-400 font-medium">Prêt</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ) : (
          messages.map(renderMessage)
        )}

        {/* Indicateur de chargement amélioré */}
        {isLoading && (
          <div className="flex justify-start mb-6 animate-in slide-in-from-bottom-2">
            <div className="flex items-start gap-3">
              <Avatar className="w-12 h-12 ring-2 ring-purple-500/20">
                <div
                  className={`w-full h-full bg-gradient-to-br ${agents.find((a) => a.id === selectedAgent)?.color} flex items-center justify-center rounded-full relative overflow-hidden`}
                >
                  <Wand2 className="w-6 h-6 text-white animate-spin" />
                  <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent" />
                </div>
              </Avatar>
              <Card className="bg-card/80 backdrop-blur-sm border border-purple-200/50 shadow-lg dark:border-purple-800/50">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-violet-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {agents.find((a) => a.id === selectedAgent)?.name} analyse votre demande...
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </ScrollArea>

      {/* Zone de saisie ultra moderne */}
      <div className="p-6 bg-card/80 backdrop-blur-sm border-t border-purple-200/50 dark:border-purple-800/50">
        <div className="flex gap-4 items-end">
          <div className="flex-1 relative">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Posez votre question à ${agents.find((a) => a.id === selectedAgent)?.name}...`}
              onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              disabled={isLoading}
              className="min-h-[56px] text-base border-2 border-purple-200/50 focus:border-purple-500 dark:border-purple-800/50 dark:focus:border-purple-400 rounded-2xl px-6 py-4 resize-none bg-background/50 backdrop-blur-sm"
            />
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
              <Sparkles className="w-5 h-5 text-purple-400 animate-pulse" />
            </div>
          </div>
          <Button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            size="lg"
            className="bg-gradient-to-r from-purple-500 via-violet-500 to-indigo-500 hover:from-purple-600 hover:via-violet-600 hover:to-indigo-600 text-white border-0 rounded-2xl px-8 py-4 shadow-lg hover:shadow-xl transition-all duration-300 min-h-[56px] pulse-glow"
          >
            {isLoading ? <Zap className="w-6 h-6 animate-spin" /> : <Send className="w-6 h-6" />}
          </Button>
        </div>

        <div className="text-xs text-muted-foreground mt-4 text-center flex items-center justify-center gap-2">
          <Stars className="w-3 h-3 text-purple-500" />
          Propulsé par l'IA NextGen - Sécurisé, intelligent et innovant
          <Stars className="w-3 h-3 text-purple-500" />
        </div>
      </div>
    </div>
  )
}
