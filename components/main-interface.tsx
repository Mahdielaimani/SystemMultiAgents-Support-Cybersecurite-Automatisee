"use client"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Send, MessageSquare, User, Activity, Sparkles, Shield, Moon, Sun, Zap, Brain } from "lucide-react"

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



// Robot Gardien Avancé et Professionnel - Dans la zone de séparation
const AdvancedGuardianRobot = ({ isDark }: { isDark: boolean }) => {
  const [position, setPosition] = useState({ x: 10, y: 50 })
  const [direction, setDirection] = useState(1)
  const [scanMode, setScanMode] = useState(false)
  const [alertLevel, setAlertLevel] = useState(0)

  useEffect(() => {
    const moveInterval = setInterval(() => {
      setPosition((prev) => {
        let newX = prev.x + direction * 0.4
        let newDirection = direction

        if (newX >= 85) {
          newDirection = -1
          newX = 85
        } else if (newX <= 15) {
          newDirection = 1
          newX = 15
        }

        setDirection(newDirection)
        return { x: newX, y: prev.y }
      })
    }, 120)

    // Mode scan aléatoire
    const scanInterval = setInterval(() => {
      setScanMode((prev) => !prev)
    }, 3000)

    // Simulation d'alertes
    const alertInterval = setInterval(() => {
      setAlertLevel(Math.floor(Math.random() * 3))
    }, 5000)

    return () => {
      clearInterval(moveInterval)
      clearInterval(scanInterval)
      clearInterval(alertInterval)
    }
  }, [direction])

  const getStatusColor = () => {
    switch (alertLevel) {
      case 0:
        return "from-green-400 to-green-600" // Sécurisé
      case 1:
        return "from-yellow-400 to-orange-500" // Surveillance
      case 2:
        return "from-red-400 to-red-600" // Alerte
      default:
        return "from-blue-400 to-blue-600"
    }
  }

  const getStatusText = () => {
    switch (alertLevel) {
      case 0:
        return "🛡️ SÉCURISÉ"
      case 1:
        return "⚠️ SURVEILLANCE"
      case 2:
        return "🚨 ALERTE"
      default:
        return "🔍 SCAN"
    }
  }

  return (
    <div
      className="absolute z-30 transition-all duration-300 ease-in-out"
      style={{
        left: `${position.x}%`,
        bottom: "-10px",
        transform: direction === -1 ? "scaleX(-1)" : "scaleX(1)",
      }}
    >
      <div className="relative group">
        {/* Corps principal du robot - Plus petit pour la zone de séparation */}
        <div
          className={`relative w-12 h-16 bg-gradient-to-b ${getStatusColor()} rounded-2xl shadow-2xl border-2 ${
            isDark ? "border-gray-600" : "border-white/30"
          }`}
        >
          {/* Tête avec écran */}
          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
            <div className="w-9 h-6 bg-gradient-to-b from-gray-800 to-gray-900 rounded-t-xl border-2 border-gray-600">
              {/* Écran avec données */}
              <div className="w-full h-full bg-black rounded-t-lg p-0.5 flex flex-col justify-center items-center">
                <div className="text-green-400 text-[5px] font-mono leading-tight">
                  <div className="animate-pulse">CPU: 98%</div>
                  <div className="animate-pulse">MEM: 76%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Antennes */}
          <div className="absolute -top-5 left-1.5">
            <div className="w-0.5 h-2 bg-gray-400 rounded-full">
              <div className="w-1.5 h-1.5 bg-red-500 rounded-full -ml-0.5 animate-pulse"></div>
            </div>
          </div>
          <div className="absolute -top-5 right-1.5">
            <div className="w-0.5 h-2 bg-gray-400 rounded-full">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full -ml-0.5 animate-pulse"></div>
            </div>
          </div>

          {/* Panneau de contrôle central */}
          <div className="absolute top-1.5 left-1/2 transform -translate-x-1/2 w-8 h-10 bg-gray-900 rounded-lg border border-gray-600">
            {/* Écran principal */}
            <div className="w-full h-6 bg-black rounded-t-lg p-0.5">
              <div className="grid grid-cols-3 gap-0.5 h-full">
                <div className="bg-green-500 rounded-sm animate-pulse"></div>
                <div className="bg-blue-500 rounded-sm animate-pulse" style={{ animationDelay: "0.2s" }}></div>
                <div className="bg-yellow-500 rounded-sm animate-pulse" style={{ animationDelay: "0.4s" }}></div>
                <div className="bg-red-500 rounded-sm animate-pulse" style={{ animationDelay: "0.6s" }}></div>
                <div className="bg-purple-500 rounded-sm animate-pulse" style={{ animationDelay: "0.8s" }}></div>
                <div className="bg-cyan-500 rounded-sm animate-pulse" style={{ animationDelay: "1s" }}></div>
              </div>
            </div>

            {/* Boutons de contrôle */}
            <div className="flex justify-center gap-1 mt-0.5">
              <div className="w-1 h-1 bg-green-400 rounded-full animate-pulse"></div>
              <div className="w-1 h-1 bg-red-400 rounded-full animate-pulse"></div>
            </div>
          </div>

          {/* Bras articulés */}
          <div className="absolute left-0 top-3 -ml-1.5">
            <div className="w-3 h-1.5 bg-gray-700 rounded-full transform rotate-12 origin-right">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full ml-1.5 animate-pulse"></div>
            </div>
          </div>
          <div className="absolute right-0 top-3 -mr-1.5">
            <div className="w-3 h-1.5 bg-gray-700 rounded-full transform -rotate-12 origin-left">
              <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse"></div>
            </div>
          </div>

          {/* Capteurs latéraux */}
          <div className="absolute left-0 top-6 w-1.5 h-0.5 bg-yellow-400 rounded-r-full animate-pulse"></div>
          <div className="absolute right-0 top-6 w-1.5 h-0.5 bg-yellow-400 rounded-l-full animate-pulse"></div>

          {/* Base avec chenilles */}
          <div className="absolute -bottom-1.5 left-1/2 transform -translate-x-1/2 w-10 h-3 bg-gray-800 rounded-full border-2 border-gray-600">
            <div className="flex justify-between items-center h-full px-0.5">
              <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-spin"></div>
              <div
                className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-spin"
                style={{ animationDelay: "0.5s" }}
              ></div>
              <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-spin" style={{ animationDelay: "1s" }}></div>
            </div>
          </div>

          {/* Rayon de scan */}
          {scanMode && (
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-24 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-70 animate-pulse"></div>
          )}
        </div>

        {/* Panneau de statut flottant */}
        <div
          className={`absolute -top-12 -left-6 ${
            isDark ? "bg-gray-800/90" : "bg-black/90"
          } backdrop-blur-sm text-white px-2 py-1 rounded-lg text-[10px] font-mono border ${
            isDark ? "border-gray-600" : "border-gray-600"
          } opacity-0 group-hover:opacity-100 transition-opacity`}
        >
          <div className="flex items-center gap-1">
            <div className={`w-1.5 h-1.5 rounded-full bg-gradient-to-r ${getStatusColor()} animate-pulse`}></div>
            <span>{getStatusText()}</span>
          </div>
          <div className="text-gray-400 text-[8px] mt-0.5">
            ID: GRD-
            {Math.floor(Math.random() * 9999)
              .toString()
              .padStart(4, "0")}
          </div>
        </div>

        {/* Effet de particules */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="absolute w-0.5 h-0.5 bg-cyan-400 rounded-full animate-ping opacity-30"
              style={{
                left: `${Math.cos((i * 90 * Math.PI) / 180) * 15}px`,
                top: `${Math.sin((i * 90 * Math.PI) / 180) * 15}px`,
                animationDelay: `${i * 0.3}s`,
                animationDuration: "2s",
              }}
            ></div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Composant Toggle Theme
const ThemeToggle = ({ isDark, setIsDark }: { isDark: boolean; setIsDark: (value: boolean) => void }) => {
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => setIsDark(!isDark)}
      className="flex items-center gap-2 text-white/80 hover:text-white hover:bg-white/10 transition-colors"
    >
      {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      <span className="text-xs">{isDark ? "Mode Clair" : "Mode Sombre"}</span>
    </Button>
  )
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<string>("support")
  const [isDark, setIsDark] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const agents: Agent[] = [
    {
      id: "support",
      name: "Agents Support",
      type: "support",
      status: "active",
      icon: MessageSquare,
      color: "bg-green-500",
      description: "Support technique TeamSquare 24/7",
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
          session_id: "default",
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
        content: "Désolé, je rencontre des difficultés techniques. Veuillez réessayer.",
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
      <div key={message.id} className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
        <div className={`max-w-[80%] ${isUser ? "order-2" : "order-1"}`}>
          <div className="flex items-start gap-3">
            {!isUser && (
              <Avatar className="w-10 h-10">
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
                    <span className={`text-sm font-medium ${isDark ? "text-gray-300" : "text-gray-700"}`}>
                      {agent.name}
                    </span>
                    <div className="w-2 h-2 bg-green-400 rounded-full" />
                  </div>
                )}

                <div className={`text-sm ${isUser ? "text-white" : isDark ? "text-gray-100" : "text-gray-900"}`}>
                  {message.content}
                </div>

                {message.metadata && !isUser && (
                  <div className="mt-2">
                    <Badge variant="secondary" className="text-xs">
                      {message.metadata.source || "assistant"}
                    </Badge>
                  </div>
                )}
              </CardContent>
            </Card>

            {isUser && (
              <Avatar className="w-10 h-10">
                <AvatarFallback className="bg-blue-500 text-white">
                  <User className="w-5 h-5" />
                </AvatarFallback>
              </Avatar>
            )}
          </div>

          <div
            className={`text-xs ${isDark ? "text-gray-400" : "text-gray-500"} mt-1 ${isUser ? "text-right mr-13" : "ml-13"}`}
          >
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      className={`flex flex-col h-screen relative transition-colors duration-300 ${isDark ? "bg-gray-900" : "bg-gray-50"}`}
    >
      {/* En-tête avec statuts et contrôles */}
      <div
        className={`py-8 border-b transition-colors duration-300 text-center relative ${
          isDark
            ? "bg-gradient-to-r from-gray-800 to-gray-700 border-gray-700"
            : "bg-gradient-to-r from-blue-600 to-purple-600"
        } text-white`}
      >
        {/* Contrôles en haut à droite */}
        <div className="absolute top-4 right-4 flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-3 py-1">
            <Activity className="w-4 h-4 text-green-300" />
            <span className="text-sm text-green-200 font-medium">En ligne</span>
          </div>
          <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-3 py-1">
            <Shield className="w-4 h-4 text-blue-200" />
            <span className="text-sm text-blue-200 font-medium">Gardien Actif</span>
          </div>
          <ThemeToggle isDark={isDark} setIsDark={setIsDark} />
        </div>

        {/* Contenu principal centré */}
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-center gap-3 mb-3">
            <Sparkles className="w-8 h-8 text-white" />
            <h1 className="text-3xl font-bold text-white">SUPPORT & SÉCURITÉ 24/7</h1>
          </div>

          {/* Badge AI Innovante et Attirante Advanced */}
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="flex items-center gap-2 bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm rounded-full px-4 py-2 border border-white/20">
              <Brain className="w-5 h-5 text-purple-200" />
              <span className="text-sm font-semibold text-purple-100">AI Innovante</span>
            </div>
            <div className="flex items-center gap-2 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 backdrop-blur-sm rounded-full px-4 py-2 border border-white/20">
              <Zap className="w-5 h-5 text-cyan-200" />
              <span className="text-sm font-semibold text-cyan-100">ATTIRANTE Advanced</span>
            </div>
          </div>

          <p className={`${isDark ? "text-gray-300" : "text-blue-100"} text-sm leading-relaxed max-w-2xl mx-auto`}>
            Support client intelligent et protection continue contre les menaces numériques, sans interruption.
          </p>
          <p className={`${isDark ? "text-gray-400" : "text-blue-100/80"} text-xs mt-1 max-w-2xl mx-auto`}>
            Grâce à notre système multi-agents TeamSquare AI, vos utilisateurs sont accompagnés et vos données
            surveillées en permanence. L'assistance devient plus rapide, la cybersécurité plus proactive.
          </p>
        </div>
      </div>

      {/* Zone de séparation avec robot */}
      <div
        className={`relative h-16 ${isDark ? "bg-gray-800" : "bg-gray-100"} border-b ${isDark ? "border-gray-700" : "border-gray-200"}`}
      >
        {/* Robot Gardien dans la zone de séparation */}
        <AdvancedGuardianRobot isDark={isDark} />
      </div>

      {/* Zone de messages */}
      <ScrollArea className="flex-1 p-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <MessageSquare className="w-10 h-10 text-white" />
            </div>
            <h2 className={`text-3xl font-bold mb-3 ${isDark ? "text-white" : "text-gray-900"}`}>
              🤖 Agents Support TeamSquare
            </h2>
            <p className={`mb-2 max-w-lg mx-auto text-lg ${isDark ? "text-gray-300" : "text-gray-600"}`}>
              Support technique intelligent 24/7
            </p>
            <p className={`mb-8 max-w-2xl mx-auto ${isDark ? "text-gray-400" : "text-gray-500"}`}>
              Notre équipe d'agents support IA vous accompagne en permanence. Posez vos questions techniques, demandez
              de l'aide ou signalez un problème - nous sommes là pour vous aider rapidement et efficacement.
            </p>

            <Card
              className={`max-w-md mx-auto hover:shadow-md transition-shadow ${
                isDark ? "bg-gray-800 border-gray-700" : "bg-white"
              }`}
            >
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <h3 className={`font-medium mb-2 ${isDark ? "text-white" : "text-gray-900"}`}>Agents Support</h3>
                <p className={`text-sm ${isDark ? "text-gray-400" : "text-gray-600"}`}>
                  Support technique TeamSquare 24/7
                </p>
                <div className="flex items-center justify-center gap-2 mt-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span className="text-xs text-green-600 font-medium">Disponible maintenant</span>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          messages.map(renderMessage)
        )}

        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="flex items-start gap-3">
              <Avatar className="w-10 h-10">
                <div className="w-full h-full bg-green-500 flex items-center justify-center rounded-full">
                  <MessageSquare className="w-5 h-5 text-white animate-pulse" />
                </div>
              </Avatar>
              <Card
                className={`${isDark ? "bg-gray-800 border-gray-700 text-white" : "bg-white border border-gray-200"}`}
              >
                <CardContent className="p-3">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" />
                      <div
                        className="w-2 h-2 bg-green-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      />
                      <div
                        className="w-2 h-2 bg-green-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      />
                    </div>
                    <span className={`text-sm ${isDark ? "text-gray-300" : "text-gray-600"}`}>
                      Agents Support analyse votre demande...
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </ScrollArea>

      {/* Zone de saisie centrée */}
      <div
        className={`p-6 border-t transition-colors duration-300 ${isDark ? "bg-gray-800 border-gray-700" : "bg-white border-gray-200"}`}
      >
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Décrivez votre problème ou posez votre question technique..."
                onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                disabled={isLoading}
                className={`min-h-[52px] text-base transition-colors duration-300 rounded-xl ${
                  isDark
                    ? "bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-green-500"
                    : "bg-white border-gray-300 text-gray-900 focus:border-green-500"
                }`}
              />
            </div>
            <Button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              size="lg"
              className="bg-green-500 hover:bg-green-600 text-white min-h-[52px] px-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </Button>
          </div>

          <div
            className={`text-xs mt-3 text-center transition-colors duration-300 ${isDark ? "text-gray-400" : "text-gray-500"}`}
          >
            Agents Support TeamSquare - Assistance technique 24/7 • AI Innovante & ATTIRANTE Advanced
          </div>
        </div>
      </div>
    </div>
  )
}



