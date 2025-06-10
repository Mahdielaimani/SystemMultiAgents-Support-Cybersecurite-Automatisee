// app/page.tsx - Version simplifiée pour utilisateurs
"use client"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Send, MessageSquare, User, Activity, Sparkles, Shield, Moon, Sun, Zap, Brain, Settings } from "lucide-react"
import { useRouter } from "next/navigation"

interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: string
  agent?: "support"
  metadata?: {
    source?: string
    agent?: string
    confidence?: number
  }
}

interface Agent {
  id: string
  name: string
  type: "support"
  status: "active" | "inactive"
  icon: any
  color: string
  description: string
}

export default function Home() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<string>("support")
  const [isDark, setIsDark] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const agents: Agent[] = [
    {
      id: "support",
      name: "Agent Support TeamSquare",
      type: "support",
      status: "active",
      icon: MessageSquare,
      color: "bg-blue-500",
      description: "Support technique et commercial 24/7",
    }
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

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
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          session_id: "default",
        }),
      })

      if (response.ok) {
        const data = await response.json()
        
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.content,
          sender: "assistant",
          timestamp: new Date().toISOString(),
          agent: selectedAgent as any,
          metadata: data.metadata,
        }

        setMessages((prev) => [...prev, assistantMessage])
      } else {
        throw new Error("Erreur de communication")
      }
    } catch (error) {
      console.error("Erreur:", error)
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Désolé, je rencontre un problème technique. Veuillez réessayer.",
        sender: "assistant",
        timestamp: new Date().toISOString(),
        agent: selectedAgent as any,
        metadata: { source: "error" },
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
      <div key={message.id} className="w-full flex justify-center mb-4">
        <div className="w-full max-w-4xl px-4">
          <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[75%] ${isUser ? "order-2" : "order-1"}`}>
              <div className="flex items-start gap-3">
                {!isUser && (
                  <Avatar className="w-10 h-10 flex-shrink-0">
                    <div className={`w-full h-full ${agent.color} flex items-center justify-center rounded-full`}>
                      <agent.icon className="w-5 h-5 text-white" />
                    </div>
                  </Avatar>
                )}

                <Card
                  className={`${
                    isUser
                      ? "bg-blue-500 text-white border-0"
                      : isDark
                      ? "bg-gray-800 border-gray-700 text-white"
                      : "bg-white border border-gray-200"
                  }`}
                >
                  <CardContent className="p-3">
                    {!isUser && (
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`text-sm font-medium ${
                          isDark ? "text-gray-300" : "text-gray-700"
                        }`}>
                          {agent.name}
                        </span>
                        <div className="w-2 h-2 bg-green-400 rounded-full" />
                      </div>
                    )}

                    <div className={`text-sm whitespace-pre-wrap ${
                      isUser ? "text-white" : isDark ? "text-gray-100" : "text-gray-900"
                    }`}>
                      {message.content}
                    </div>

                    {message.metadata && !isUser && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        <Badge variant="secondary" className="text-xs">
                          {message.metadata.source || "assistant"}
                        </Badge>
                        {message.metadata.confidence && (
                          <Badge variant="outline" className="text-xs">
                            Confiance: {(message.metadata.confidence * 100).toFixed(0)}%
                          </Badge>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {isUser && (
                  <Avatar className="w-10 h-10 flex-shrink-0">
                    <AvatarFallback className="bg-blue-500 text-white">
                      <User className="w-5 h-5" />
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>

              <div
                className={`text-xs ${isDark ? "text-gray-400" : "text-gray-500"} mt-1 ${
                  isUser ? "text-right mr-13" : "ml-13"
                }`}
              >
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      className={`flex flex-col h-screen relative transition-colors duration-300 ${
        isDark ? "bg-gray-900" : "bg-gray-50"
      }`}
    >
      {/* En-tête avec contrôles */}
      <div
        className={`py-8 border-b transition-colors duration-300 text-center relative ${
          isDark
            ? "bg-gradient-to-r from-gray-800 to-gray-700 border-gray-700"
            : "bg-gradient-to-r from-blue-600 to-purple-600"
        } text-white`}
      >
        {/* Contrôles en haut à droite */}
        <div className="absolute top-4 right-4 flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsDark(!isDark)}
            className="text-white hover:bg-white/20"
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/admin-security")}
            className="text-white hover:bg-white/20"
          >
            <Settings className="w-5 h-5" />
            <span className="ml-2">Admin</span>
          </Button>
        </div>

        <h1 className="text-4xl font-bold mb-2">TeamSquare Assistant IA</h1>
        <p className="text-xl opacity-90">Support intelligent pour votre équipe</p>

        {/* Indicateur de statut */}
        <div className="absolute bottom-4 left-4 flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-900/50 border border-green-500">
            <Shield className="w-4 h-4" />
            <span className="text-sm font-medium">Système sécurisé</span>
          </div>
        </div>
      </div>

      {/* Zone principale avec agent et chat */}
      <div className="flex flex-1 overflow-hidden">
        {/* Panneau latéral de l'agent */}
        <div
          className={`w-80 transition-colors duration-300 ${
            isDark ? "bg-gray-800 border-gray-700" : "bg-white"
          } border-r p-6 overflow-y-auto`}
        >
          <h2 className={`text-2xl font-bold mb-6 ${isDark ? "text-white" : "text-gray-900"}`}>
            Assistant IA
          </h2>

          <div className="space-y-4">
            {agents.map((agent) => (
              <Card
                key={agent.id}
                className={`cursor-pointer transition-all transform hover:scale-105 ${
                  selectedAgent === agent.id
                    ? "ring-2 ring-blue-500 shadow-lg"
                    : ""
                } ${
                  isDark ? "bg-gray-700 hover:bg-gray-600" : "hover:shadow-md"
                }`}
                onClick={() => setSelectedAgent(agent.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className={`p-3 rounded-full ${agent.color}`}>
                      <agent.icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className={`font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>
                          {agent.name}
                        </h3>
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 rounded-full bg-green-400" />
                          <span className={`text-xs ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                            En ligne
                          </span>
                        </div>
                      </div>
                      <p className={`text-sm ${isDark ? "text-gray-300" : "text-gray-600"}`}>
                        {agent.description}
                      </p>
                      <div className="mt-2 space-y-1 text-xs">
                        <div className="flex items-center gap-2">
                          <Activity className="w-3 h-3" />
                          <span>Réponses en temps réel</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Brain className="w-3 h-3" />
                          <span>IA hybride avancée</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Sparkles className="w-3 h-3" />
                          <span>Mémoire conversationnelle</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Informations sur TeamSquare */}
          <div className="mt-6 p-4 bg-blue-500/10 border-2 border-blue-500/30 rounded-lg">
            <h3 className={`font-semibold mb-3 ${isDark ? "text-white" : "text-gray-900"}`}>
              À propos de TeamSquare
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className={isDark ? "text-gray-300" : "text-gray-600"}>Plateforme</span>
                <span className="font-medium text-blue-500">Collaboration</span>
              </div>
              <div className="flex justify-between">
                <span className={isDark ? "text-gray-300" : "text-gray-600"}>Fonctionnalités</span>
                <span className="font-medium text-green-500">30+</span>
              </div>
              <div className="flex justify-between">
                <span className={isDark ? "text-gray-300" : "text-gray-600"}>Support</span>
                <span className="font-medium text-purple-500">24/7</span>
              </div>
            </div>
          </div>
        </div>

        {/* Zone de chat */}
        <div className="flex-1 flex flex-col">
          <ScrollArea className="flex-1 py-6">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center max-w-md">
                  <MessageSquare className={`w-16 h-16 mx-auto mb-4 ${isDark ? "text-gray-600" : "text-gray-400"}`} />
                  <h3 className={`text-xl font-semibold mb-2 ${isDark ? "text-white" : "text-gray-900"}`}>
                    Bienvenue sur TeamSquare Assistant
                  </h3>
                  <p className={`${isDark ? "text-gray-400" : "text-gray-600"} mb-4`}>
                    Notre assistant IA est là pour vous aider avec toutes vos questions sur TeamSquare.
                    Demandez-moi n'importe quoi !
                  </p>
                  <div className="grid grid-cols-1 gap-2 text-sm">
                    <div className="flex items-center gap-2 justify-center">
                      <Zap className="w-4 h-4 text-yellow-500" />
                      <span>Réponses instantanées</span>
                    </div>
                    <div className="flex items-center gap-2 justify-center">
                      <Brain className="w-4 h-4 text-purple-500" />
                      <span>IA conversationnelle</span>
                    </div>
                    <div className="flex items-center gap-2 justify-center">
                      <Shield className="w-4 h-4 text-green-500" />
                      <span>Interactions sécurisées</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {messages.map(renderMessage)}
                <div ref={messagesEndRef} />
              </>
            )}
          </ScrollArea>

          {/* Zone de saisie */}
          <div
            className={`border-t transition-colors duration-300 ${
              isDark ? "bg-gray-800 border-gray-700" : "bg-white"
            } p-4`}
          >
            <div className="max-w-4xl mx-auto">
              <div className="flex gap-3">
                <Input
                  placeholder="Posez-moi une question sur TeamSquare..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSend()}
                  disabled={isLoading}
                  className={`flex-1 ${
                    isDark
                      ? "bg-gray-700 border-gray-600 text-white placeholder-gray-400"
                      : ""
                  }`}
                />
                <Button
                  onClick={handleSend}
                  disabled={isLoading || !input.trim()}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </Button>
              </div>
              
              {/* Suggestions rapides */}
              <div className="mt-3 flex flex-wrap gap-2">
                {[
                  "Quels sont les prix ?",
                  "Fonctionnalités disponibles",
                  "Comment ça marche ?",
                  "Support technique"
                ].map((suggestion) => (
                  <Button
                    key={suggestion}
                    variant="outline"
                    size="sm"
                    onClick={() => setInput(suggestion)}
                    disabled={isLoading}
                    className={`text-xs ${
                      isDark 
                        ? "border-gray-600 text-gray-300 hover:bg-gray-700" 
                        : "border-gray-300 text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}