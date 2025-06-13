// app/page.tsx - Version avec gestion d'erreurs robuste
"use client"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Send, 
  MessageSquare, 
  User, 
  Activity, 
  Sparkles, 
  Shield, 
  Moon, 
  Sun, 
  Zap, 
  Brain, 
  Settings,
  AlertTriangle,
  Wifi,
  WifiOff,
  RefreshCw
} from "lucide-react"
import { useRouter } from "next/navigation"

interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: string
  metadata?: {
    source?: string
    confidence?: number
    fallback_used?: boolean
    error?: boolean
  }
}

interface ConnectionStatus {
  backend: boolean
  fallback: boolean
  lastCheck: string
}

export default function Home() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isDark, setIsDark] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    backend: true,
    fallback: true,
    lastCheck: new Date().toISOString()
  })
  const [showConnectionAlert, setShowConnectionAlert] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Vérifier la connexion au démarrage et périodiquement
  useEffect(() => {
    checkConnection()
    const interval = setInterval(checkConnection, 60000) // Vérifier toutes les minutes
    return () => clearInterval(interval)
  }, [])

  const checkConnection = async () => {
    try {
      const response = await fetch("/api/chat", {
        method: "GET",
        signal: AbortSignal.timeout(5000)
      })
      
      const data = await response.json()
      
      setConnectionStatus({
        backend: data.status === "healthy" || response.ok,
        fallback: data.fallback_available !== false,
        lastCheck: new Date().toISOString()
      })

      // Masquer l'alerte si la connexion est rétablie
      if (response.ok) {
        setShowConnectionAlert(false)
      }
    } catch (error) {
      console.warn("Connection check failed:", error)
      setConnectionStatus(prev => ({
        ...prev,
        backend: false,
        lastCheck: new Date().toISOString()
      }))
      setShowConnectionAlert(true)
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
          metadata: {
            source: data.metadata?.source || "assistant",
            confidence: data.metadata?.confidence,
            fallback_used: data.metadata?.fallback_used || data.metadata?.local_generation
          }
        }

        setMessages((prev) => [...prev, assistantMessage])
        
        // Masquer l'alerte de connexion si la réponse arrive
        setShowConnectionAlert(false)
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      console.error("Erreur:", error)
      
      // Afficher l'alerte de connexion
      setShowConnectionAlert(true)
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Je rencontre des difficultés de connexion. Mes réponses peuvent être limitées en mode hors ligne. Veuillez vérifier votre connexion internet.",
        sender: "assistant",
        timestamp: new Date().toISOString(),
        metadata: { 
          source: "error", 
          error: true,
          fallback_used: true
        },
      }
      
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const renderMessage = (message: Message) => {
    const isUser = message.sender === "user"

    return (
      <div key={message.id} className="w-full flex justify-center mb-4">
        <div className="w-full max-w-4xl px-4">
          <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[75%] ${isUser ? "order-2" : "order-1"}`}>
              <div className="flex items-start gap-3">
                {!isUser && (
                  <Avatar className="w-10 h-10 flex-shrink-0">
                    <div className={`w-full h-full bg-blue-500 flex items-center justify-center rounded-full`}>
                      <MessageSquare className="w-5 h-5 text-white" />
                    </div>
                  </Avatar>
                )}

                <Card
                  className={`${
                    isUser
                      ? "bg-white text-black border border-gray-200 shadow-md"
                      : isDark
                      ? "bg-gray-800 border-gray-700 text-white"
                      : "bg-white border border-gray-200"
                  } ${message.metadata?.error ? "border-red-500" : ""}`}
                >
                  <CardContent className="p-3">
                    {!isUser && (
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`text-sm font-medium ${
                          isDark ? "text-gray-300" : "text-gray-700"
                        }`}>
                          AI Agent TeamSquare
                        </span>
                        <div className={`w-2 h-2 rounded-full ${
                          message.metadata?.error ? "bg-red-400" :
                          message.metadata?.fallback_used ? "bg-yellow-400" : "bg-green-400"
                        }`} />
                      </div>
                    )}

                    <div className={`text-sm whitespace-pre-wrap ${
                      isUser ? "text-black" : isDark ? "text-gray-100" : "text-gray-900"
                    }`}>
                      {message.content}
                    </div>

                    {message.metadata && !isUser && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {message.metadata.confidence && (
                          <Badge variant="outline" className="text-xs">
                            Confiance: {(message.metadata.confidence * 100).toFixed(0)}%
                          </Badge>
                        )}
                        {message.metadata.fallback_used && (
                          <Badge variant="outline" className="text-xs text-yellow-600">
                            Mode dégradé
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
      {/* Alerte de connexion */}
      {showConnectionAlert && (
        <Alert className="absolute top-4 left-4 right-4 z-50 bg-yellow-50 border-yellow-200">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>
              {!connectionStatus.backend ? "Connexion au serveur interrompue. " : ""}
              Fonctionnement en mode dégradé.
            </span>
            <Button 
              size="sm" 
              variant="outline" 
              onClick={checkConnection}
              className="ml-2"
            >
              <RefreshCw className="w-4 h-4 mr-1" />
              Réessayer
            </Button>
          </AlertDescription>
        </Alert>
      )}

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

        <h1 className="text-4xl font-bold mb-2">TeamSquare AI Agents</h1>
        <p className="text-xl opacity-90">Support intelligent pour votre équipe</p>

        {/* Indicateur de statut de connexion */}
        <div className="absolute bottom-4 left-4 flex items-center gap-2">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${
            connectionStatus.backend 
              ? "bg-green-900/50 border-green-500" 
              : "bg-red-900/50 border-red-500"
          }`}>
            {connectionStatus.backend ? (
              <>
                <Wifi className="w-4 h-4" />
                <span className="text-sm font-medium">Connecté</span>
              </>
            ) : (
              <>
                <WifiOff className="w-4 h-4" />
                <span className="text-sm font-medium">Mode hors ligne</span>
              </>
            )}
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
            AI Agents
          </h2>

          <Card
            className={`cursor-pointer transition-all transform hover:scale-105 ring-2 ring-blue-500 shadow-lg ${
              isDark ? "bg-gray-700 hover:bg-gray-600" : "hover:shadow-md"
            }`}
          >
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <div className="p-3 rounded-full bg-blue-500">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className={`font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>
                      Agents Support TeamSquare
                    </h3>
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${
                        connectionStatus.backend ? "bg-green-400" : 
                        connectionStatus.fallback ? "bg-yellow-400" : "bg-red-400"
                      }`} />
                      <span className={`text-xs ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                        {connectionStatus.backend ? "En ligne" : 
                         connectionStatus.fallback ? "Mode dégradé" : "Hors ligne"}
                      </span>
                    </div>
                  </div>
                  <p className={`text-sm ${isDark ? "text-gray-300" : "text-gray-600"}`}>
                    Support technique et commercial 24/7
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
                    {!connectionStatus.backend && (
                      <div className="flex items-center gap-2 text-yellow-600">
                        <Shield className="w-3 h-3" />
                        <span>Mode sécurisé hors ligne</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

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
              <div className="flex justify-between">
                <span className={isDark ? "text-gray-300" : "text-gray-600"}>Statut</span>
                <span className={`font-medium ${
                  connectionStatus.backend ? "text-green-500" : "text-yellow-500"
                }`}>
                  {connectionStatus.backend ? "Opérationnel" : "Mode dégradé"}
                </span>
              </div>
            </div>
          </div>

          {/* Informations de connexion */}
          <div className="mt-4 p-3 bg-gray-500/10 border border-gray-500/30 rounded-lg">
            <h4 className={`text-sm font-medium mb-2 ${isDark ? "text-white" : "text-gray-900"}`}>
              État de la connexion
            </h4>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span>Backend principal</span>
                <span className={connectionStatus.backend ? "text-green-500" : "text-red-500"}>
                  {connectionStatus.backend ? "✓ Connecté" : "✗ Déconnecté"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Mode de secours</span>
                <span className={connectionStatus.fallback ? "text-green-500" : "text-red-500"}>
                  {connectionStatus.fallback ? "✓ Disponible" : "✗ Indisponible"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Dernière vérification</span>
                <span className="text-gray-500">
                  {new Date(connectionStatus.lastCheck).toLocaleTimeString()}
                </span>
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
                    Bienvenue sur TeamSquare AI Agents
                  </h3>
                  <p className={`${isDark ? "text-gray-400" : "text-gray-600"} mb-4`}>
                    Notre AI Agents est là pour vous aider avec toutes vos questions sur TeamSquare.
                    {!connectionStatus.backend && " Actuellement en mode hors ligne avec fonctionnalités limitées."}
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
                  placeholder={
                    connectionStatus.backend 
                      ? "Posez-moi une question sur TeamSquare..."
                      : "Posez-moi une question (mode hors ligne)..."
                  }
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

              {/* Statut de connexion en bas */}
              {!connectionStatus.backend && (
                <div className="mt-2 text-center">
                  <span className="text-xs text-yellow-600">
                    Mode hors ligne - Fonctionnalités limitées disponibles
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}