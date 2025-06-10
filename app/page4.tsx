// app/page.tsx - Version avec Robot de Sécurité Intelligent
"use client"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Send, MessageSquare, User, Activity, Sparkles, Shield, Moon, Sun, Zap, Brain, AlertTriangle, Lock, ShieldAlert, FileWarning, Ban } from "lucide-react"

interface Message {
  id: string
  content: string
  sender: "user" | "assistant" | "security"
  timestamp: string
  agent?: "support" | "security"
  metadata?: {
    source?: string
    agent?: string
    confidence?: number
    threat_level?: "safe" | "warning" | "danger"
    vulnerability_type?: string
    intent_classification?: string
  }
}

interface SecurityAlert {
  id: string
  type: "vulnerability" | "network" | "intent"
  severity: "low" | "medium" | "high" | "critical"
  message: string
  timestamp: string
  action_taken: string
}

interface Agent {
  id: string
  name: string
  type: "support" | "security"
  status: "active" | "inactive" | "alert"
  icon: any
  color: string
  description: string
}

// Robot de Sécurité Intelligent avec IA
const SecurityRobot = ({ 
  isDark, 
  onThreatDetected, 
  isAnalyzing,
  threatLevel 
}: { 
  isDark: boolean
  onThreatDetected: (alert: SecurityAlert) => void
  isAnalyzing: boolean
  threatLevel: "safe" | "warning" | "danger"
}) => {
  const [position, setPosition] = useState({ x: 85, y: 20 })
  const [scanMode, setScanMode] = useState(false)
  const [robotState, setRobotState] = useState<"patrol" | "scanning" | "alert" | "blocking">("patrol")

  useEffect(() => {
    if (isAnalyzing) {
      setRobotState("scanning")
      setScanMode(true)
    } else if (threatLevel === "danger") {
      setRobotState("alert")
    } else if (threatLevel === "warning") {
      setRobotState("scanning")
    } else {
      setRobotState("patrol")
      setScanMode(false)
    }
  }, [isAnalyzing, threatLevel])

  const getStateColor = () => {
    switch (robotState) {
      case "patrol":
        return "from-blue-400 to-blue-600"
      case "scanning":
        return "from-yellow-400 to-orange-500"
      case "alert":
        return "from-red-500 to-red-700"
      case "blocking":
        return "from-purple-500 to-purple-700"
      default:
        return "from-gray-400 to-gray-600"
    }
  }

  const getStateText = () => {
    switch (robotState) {
      case "patrol":
        return "🛡️ PATROUILLE"
      case "scanning":
        return "🔍 ANALYSE EN COURS"
      case "alert":
        return "🚨 MENACE DÉTECTÉE"
      case "blocking":
        return "🚫 BLOCAGE ACTIF"
      default:
        return "⚡ ACTIF"
    }
  }

  return (
    <div
      className="fixed z-40 transition-all duration-500 ease-in-out"
      style={{
        right: `${100 - position.x}%`,
        top: `${position.y}%`,
      }}
    >
      <div className="relative group">
        {/* Corps du robot de sécurité */}
        <div
          className={`relative w-20 h-24 bg-gradient-to-b ${getStateColor()} rounded-3xl shadow-2xl border-2 ${
            isDark ? "border-gray-600" : "border-white/30"
          } ${robotState === "alert" ? "animate-pulse" : ""}`}
        >
          {/* Tête avec écran de sécurité */}
          <div className="absolute -top-5 left-1/2 transform -translate-x-1/2">
            <div className="w-16 h-10 bg-gradient-to-b from-gray-900 to-black rounded-t-2xl border-2 border-red-600">
              <div className="w-full h-full bg-black rounded-t-xl p-1 flex flex-col justify-center items-center">
                <div className="text-red-400 text-[8px] font-mono leading-tight text-center">
                  <div className="animate-pulse">SECURITY AI</div>
                  <div className={`${robotState === "alert" ? "text-red-600 animate-flash" : "text-green-400"}`}>
                    {robotState.toUpperCase()}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Antennes de détection */}
          <div className="absolute -top-8 left-3">
            <div className="w-1 h-4 bg-red-500 rounded-full">
              <div className={`w-3 h-3 ${robotState === "alert" ? "bg-red-600" : "bg-green-500"} rounded-full -ml-1 animate-pulse`}></div>
            </div>
          </div>
          <div className="absolute -top-8 right-3">
            <div className="w-1 h-4 bg-blue-500 rounded-full">
              <div className={`w-3 h-3 ${robotState === "scanning" ? "bg-yellow-500" : "bg-blue-500"} rounded-full -ml-1 animate-pulse`}></div>
            </div>
          </div>

          {/* Panneau central de sécurité */}
          <div className="absolute top-3 left-1/2 transform -translate-x-1/2 w-14 h-16 bg-black rounded-xl border-2 border-red-600">
            {/* Écran d'analyse */}
            <div className="w-full h-10 bg-black rounded-t-lg p-1">
              {robotState === "alert" ? (
                <div className="w-full h-full flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-red-500 animate-pulse" />
                </div>
              ) : robotState === "scanning" ? (
                <div className="grid grid-cols-3 gap-0.5 h-full">
                  {[...Array(9)].map((_, i) => (
                    <div
                      key={i}
                      className={`${
                        i % 3 === 0 ? "bg-green-500" : i % 3 === 1 ? "bg-yellow-500" : "bg-red-500"
                      } rounded-sm animate-pulse`}
                      style={{ animationDelay: `${i * 0.1}s` }}
                    ></div>
                  ))}
                </div>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Shield className="w-6 h-6 text-green-500" />
                </div>
              )}
            </div>

            {/* Indicateurs de sécurité */}
            <div className="flex justify-center gap-1 mt-1">
              <div className={`w-2 h-2 ${robotState === "alert" ? "bg-red-600" : "bg-green-400"} rounded-full animate-pulse`}></div>
              <div className={`w-2 h-2 ${robotState === "scanning" ? "bg-yellow-400" : "bg-blue-400"} rounded-full animate-pulse`}></div>
              <div className={`w-2 h-2 ${robotState === "blocking" ? "bg-purple-400" : "bg-gray-400"} rounded-full`}></div>
            </div>
          </div>

          {/* Bras armés */}
          <div className="absolute left-0 top-6 -ml-3">
            <div className="w-6 h-3 bg-gray-800 rounded-full transform rotate-12 origin-right">
              <div className={`w-3 h-3 ${robotState === "alert" ? "bg-red-500" : "bg-blue-500"} rounded-full ml-3 animate-pulse`}></div>
            </div>
          </div>
          <div className="absolute right-0 top-6 -mr-3">
            <div className="w-6 h-3 bg-gray-800 rounded-full transform -rotate-12 origin-left">
              <div className={`w-3 h-3 ${robotState === "blocking" ? "bg-purple-500" : "bg-green-500"} rounded-full animate-pulse`}></div>
            </div>
          </div>

          {/* Scanners latéraux */}
          <div className="absolute left-0 top-12 w-3 h-1 bg-red-600 rounded-r-full animate-pulse"></div>
          <div className="absolute right-0 top-12 w-3 h-1 bg-red-600 rounded-l-full animate-pulse"></div>

          {/* Base mobile renforcée */}
          <div className="absolute -bottom-3 left-1/2 transform -translate-x-1/2 w-16 h-5 bg-gray-900 rounded-full border-2 border-red-600">
            <div className="flex justify-between items-center h-full px-1">
              <div className="w-2 h-2 bg-red-400 rounded-full animate-spin"></div>
              <div className="w-2 h-2 bg-red-400 rounded-full animate-spin" style={{ animationDelay: "0.3s" }}></div>
              <div className="w-2 h-2 bg-red-400 rounded-full animate-spin" style={{ animationDelay: "0.6s" }}></div>
            </div>
          </div>

          {/* Rayon de scan de sécurité */}
          {scanMode && (
            <>
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-48 h-1 bg-gradient-to-r from-transparent via-red-400 to-transparent opacity-70 animate-pulse"></div>
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 border-2 border-red-400 rounded-full opacity-30 animate-ping"></div>
            </>
          )}
        </div>

        {/* Panneau d'état de sécurité */}
        <div
          className={`absolute -top-20 -left-12 ${
            isDark ? "bg-gray-900/95" : "bg-black/95"
          } backdrop-blur-sm text-white px-4 py-3 rounded-xl text-xs font-mono border-2 ${
            robotState === "alert" ? "border-red-600" : "border-gray-600"
          } ${robotState === "alert" ? "opacity-100" : "opacity-0 group-hover:opacity-100"} transition-opacity`}
        >
          <div className="flex items-center gap-2 mb-1">
            <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${getStateColor()} animate-pulse`}></div>
            <span className="font-bold">{getStateText()}</span>
          </div>
          <div className="text-gray-400 text-[10px] space-y-1">
            <div>ID: SEC-AI-2024</div>
            <div>Modèles actifs: 3/3</div>
            <div>Dernière analyse: {new Date().toLocaleTimeString()}</div>
          </div>
        </div>

        {/* Effets visuels de sécurité */}
        {robotState === "alert" && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32">
              <div className="w-full h-full border-4 border-red-500 rounded-full animate-pulse opacity-50"></div>
              <div className="absolute inset-0 w-full h-full border-4 border-red-400 rounded-full animate-ping"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Panneau d'alertes de sécurité
const SecurityPanel = ({ 
  alerts, 
  isDark 
}: { 
  alerts: SecurityAlert[]
  isDark: boolean 
}) => {
  if (alerts.length === 0) return null

  return (
    <div className="fixed top-24 right-4 w-96 z-50">
      <Card className={`${isDark ? "bg-gray-900 border-red-600" : "bg-white border-red-500"} border-2 shadow-2xl`}>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <ShieldAlert className="w-5 h-5 text-red-500" />
            <h3 className={`font-bold ${isDark ? "text-white" : "text-gray-900"}`}>
              Alertes de Sécurité ({alerts.length})
            </h3>
          </div>
          <ScrollArea className="h-64">
            <div className="space-y-2">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-lg ${
                    alert.severity === "critical"
                      ? "bg-red-500/20 border border-red-500"
                      : alert.severity === "high"
                      ? "bg-orange-500/20 border border-orange-500"
                      : alert.severity === "medium"
                      ? "bg-yellow-500/20 border border-yellow-500"
                      : "bg-blue-500/20 border border-blue-500"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge
                          variant={alert.severity === "critical" ? "destructive" : "secondary"}
                          className="text-xs"
                        >
                          {alert.type.toUpperCase()}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          {new Date(alert.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className={`text-sm ${isDark ? "text-gray-200" : "text-gray-700"}`}>
                        {alert.message}
                      </p>
                      <p className={`text-xs mt-1 ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                        Action: {alert.action_taken}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}

// Composant principal avec intégration de sécurité
export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<string>("support")
  const [isDark, setIsDark] = useState(false)
  const [isSystemBlocked, setIsSystemBlocked] = useState(false)
  const [securityAlerts, setSecurityAlerts] = useState<SecurityAlert[]>([])
  const [threatLevel, setThreatLevel] = useState<"safe" | "warning" | "danger">("safe")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const agents: Agent[] = [
    {
      id: "support",
      name: "Agent Support",
      type: "support",
      status: isSystemBlocked ? "inactive" : "active",
      icon: MessageSquare,
      color: "bg-green-500",
      description: "Support technique TeamSquare 24/7",
    },
    {
      id: "security",
      name: "Agent Sécurité",
      type: "security",
      status: threatLevel === "danger" ? "alert" : "active",
      icon: Shield,
      color: "bg-red-500",
      description: "Protection et analyse de sécurité",
    },
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Analyse de sécurité du message
  const analyzeMessageSecurity = async (message: string) => {
    setIsAnalyzing(true)
    
    try {
      // Appel à l'API de cybersécurité
      const response = await fetch("/api/cybersecurity/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          text: message,
          models: ["vulnerability_classifier", "network_analyzer", "intent_classifier"]
        }),
      })

      if (response.ok) {
        const analysis = await response.json()
        
        // Vérifier les menaces
        const vulnerabilityResult = analysis.vulnerability_classifier
        const networkResult = analysis.network_analyzer
        const intentResult = analysis.intent_classifier

        let hasThreats = false
        let alerts: SecurityAlert[] = []

        // Vérifier les vulnérabilités
        if (vulnerabilityResult && vulnerabilityResult.vulnerability_type !== "SAFE") {
          hasThreats = true
          alerts.push({
            id: Date.now().toString(),
            type: "vulnerability",
            severity: vulnerabilityResult.confidence > 0.8 ? "critical" : "high",
            message: `Vulnérabilité détectée: ${vulnerabilityResult.vulnerability_type}`,
            timestamp: new Date().toISOString(),
            action_taken: "Message bloqué et agent support notifié"
          })
        }

        // Vérifier le trafic réseau
        if (networkResult && networkResult.traffic_type !== "NORMAL") {
          hasThreats = true
          alerts.push({
            id: (Date.now() + 1).toString(),
            type: "network",
            severity: networkResult.traffic_type === "DDOS" ? "critical" : "high",
            message: `Activité réseau suspecte: ${networkResult.traffic_type}`,
            timestamp: new Date().toISOString(),
            action_taken: "Surveillance réseau activée"
          })
        }

        // Vérifier l'intention
        if (intentResult && intentResult.intent === "Malicious") {
          hasThreats = true
          alerts.push({
            id: (Date.now() + 2).toString(),
            type: "intent",
            severity: intentResult.confidence > 0.5 ? "high" : "medium",
            message: `Intention malveillante détectée (confiance: ${(intentResult.confidence * 100).toFixed(0)}%)`,
            timestamp: new Date().toISOString(),
            action_taken: "Conversation surveillée"
          })
        }

        return { hasThreats, alerts, analysis }
      }
    } catch (error) {
      console.error("Erreur analyse sécurité:", error)
    } finally {
      setIsAnalyzing(false)
    }

    return { hasThreats: false, alerts: [], analysis: null }
  }

  // Gestionnaire de menaces détectées
  const handleThreatDetected = (alert: SecurityAlert) => {
    setSecurityAlerts((prev) => [alert, ...prev])
    
    if (alert.severity === "critical") {
      setThreatLevel("danger")
      setIsSystemBlocked(true)
      
      // Message de sécurité automatique
      const securityMessage: Message = {
        id: Date.now().toString(),
        content: `🚨 ALERTE SÉCURITÉ: ${alert.message}\n\n⚠️ Le système a été verrouillé par mesure de sécurité. L'agent support a été notifié et la conversation est suspendue.\n\n📊 Un rapport détaillé a été généré.`,
        sender: "security",
        timestamp: new Date().toISOString(),
        agent: "security",
        metadata: {
          threat_level: "danger",
          source: "security_ai"
        }
      }
      
      setMessages((prev) => [...prev, securityMessage])
    }
  }

  const handleSendMessage = async (message: string) => {
    // Analyser la sécurité d'abord
    const securityCheck = await analyzeMessageSecurity(message)
    
    if (securityCheck.hasThreats) {
      // Alertes de sécurité
      securityCheck.alerts.forEach(alert => handleThreatDetected(alert))
      
      // Bloquer le message si menace critique
      const criticalThreat = securityCheck.alerts.some(a => a.severity === "critical")
      if (criticalThreat) {
        return {
          content: "Message bloqué pour des raisons de sécurité.",
          metadata: { 
            source: "security_block",
            threat_level: "danger"
          }
        }
      }
    }

    // Si pas de menace critique, continuer avec l'agent support
    if (!isSystemBlocked) {
      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message,
            agent: selectedAgent,
            session_id: "default",
            security_analysis: securityCheck.analysis
          }),
        })

        if (response.ok) {
          const data = await response.json()
          return data
        }
      } catch (error) {
        console.error("Erreur:", error)
      }
    }

    return {
      content: "Le système est actuellement en mode sécurisé. Veuillez patienter.",
      metadata: { source: "security_mode" }
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading || isSystemBlocked) return

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
    } finally {
      setIsLoading(false)
    }
  }

  // Générer un rapport de sécurité
  const generateSecurityReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      alerts: securityAlerts,
      blocked_messages: messages.filter(m => m.metadata?.threat_level === "danger"),
      summary: `${securityAlerts.length} alertes détectées, ${securityAlerts.filter(a => a.severity === "critical").length} critiques`,
      recommendations: [
        "Renforcer les filtres de sécurité",
        "Former les utilisateurs aux bonnes pratiques",
        "Mettre à jour les modèles de détection"
      ]
    }
    
    console.log("Rapport de sécurité:", report)
    // Ici vous pouvez sauvegarder ou envoyer le rapport
    
    return report
  }

  const renderMessage = (message: Message) => {
    const isUser = message.sender === "user"
    const isSecurity = message.sender === "security"
    const agent = agents.find((a) => a.id === message.agent) || agents[0]

    return (
      <div key={message.id} className="w-full flex justify-center mb-4">
        <div className="w-full max-w-4xl px-4">
          <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[75%] ${isUser ? "order-2" : "order-1"}`}>
              <div className="flex items-start gap-3">
                {!isUser && (
                  <Avatar className="w-10 h-10 flex-shrink-0">
                    <div className={`w-full h-full ${isSecurity ? "bg-red-500" : agent.color} flex items-center justify-center rounded-full`}>
                      {isSecurity ? <Shield className="w-5 h-5 text-white" /> : <agent.icon className="w-5 h-5 text-white" />}
                    </div>
                  </Avatar>
                )}

                <Card
                  className={`${
                    isUser
                      ? "bg-blue-500 text-white border-0"
                      : isSecurity
                      ? "bg-red-500/10 border-2 border-red-500"
                      : isDark
                      ? "bg-gray-800 border-gray-700 text-white"
                      : "bg-white border border-gray-200"
                  }`}
                >
                  <CardContent className="p-3">
                    {!isUser && (
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`text-sm font-medium ${
                          isSecurity ? "text-red-600" : isDark ? "text-gray-300" : "text-gray-700"
                        }`}>
                          {isSecurity ? "Agent Sécurité AI" : agent.name}
                        </span>
                        <div className={`w-2 h-2 ${isSecurity ? "bg-red-500" : "bg-green-400"} rounded-full ${
                          isSecurity ? "animate-pulse" : ""
                        }`} />
                      </div>
                    )}

                    <div className={`text-sm whitespace-pre-wrap ${
                      isUser ? "text-white" : isSecurity ? "text-red-900" : isDark ? "text-gray-100" : "text-gray-900"
                    }`}>
                      {message.content}
                    </div>

                    {message.metadata && !isUser && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        <Badge 
                          variant={message.metadata.threat_level === "danger" ? "destructive" : "secondary"} 
                          className="text-xs"
                        >
                          {message.metadata.source || "assistant"}
                        </Badge>
                        {message.metadata.threat_level && (
                          <Badge 
                            variant="destructive" 
                            className="text-xs"
                          >
                            Niveau: {message.metadata.threat_level}
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
      {/* Robot de Sécurité Intelligent */}
      <SecurityRobot 
        isDark={isDark} 
        onThreatDetected={handleThreatDetected}
        isAnalyzing={isAnalyzing}
        threatLevel={threatLevel}
      />

      {/* Panneau d'alertes de sécurité */}
      <SecurityPanel alerts={securityAlerts} isDark={isDark} />

      {/* Robot Gardien flottant original */}
      {/* <AdvancedGuardianRobot isDark={isDark} /> */}

      {/* En-tête avec statuts et contrôles */}
      <div
        className={`py-8 border-b transition-colors duration-300 text-center relative ${
          isSystemBlocked
            ? "bg-gradient-to-r from-red-800 to-red-600"
            : isDark
            ? "bg-gradient-to-r from-gray-800 to-gray-700 border-gray-700"
            : "bg-gradient-to-r from-blue-600 to-purple-600"
        } text-white`}
      >
        {/* Contrôles en haut à droite */}
        <div className="absolute top-4 right-4 flex items-center gap-3">
          <div className={`flex items-center gap-2 ${
            isSystemBlocked ? "opacity-50" : ""
          }`}>
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
              onClick={generateSecurityReport}
              className="text-white hover:bg-white/20"
            >
              <FileWarning className="w-5 h-5" />
              <span className="ml-2">Rapport</span>
            </Button>
          </div>
        </div>

        <h1 className="text-4xl font-bold mb-2">
          {isSystemBlocked ? "🚨 SYSTÈME VERROUILLÉ" : "TeamSquare Assistant IA"}
        </h1>
        <p className="text-xl opacity-90">
          {isSystemBlocked 
            ? "Menace de sécurité détectée - Accès restreint"
            : "Support intelligent avec protection AI avancée"
          }
        </p>

        {/* Indicateur de sécurité */}
        <div className="absolute bottom-4 left-4 flex items-center gap-2">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${
            threatLevel === "danger" 
              ? "bg-red-900/50 border border-red-500" 
              : threatLevel === "warning"
              ? "bg-yellow-900/50 border border-yellow-500"
              : "bg-green-900/50 border border-green-500"
          }`}>
            <ShieldAlert className="w-4 h-4" />
            <span className="text-sm font-medium">
              Niveau de sécurité: {threatLevel === "danger" ? "CRITIQUE" : threatLevel === "warning" ? "ATTENTION" : "NORMAL"}
            </span>
          </div>
        </div>
      </div>

      {/* Zone principale avec agents et chat */}
      <div className="flex flex-1 overflow-hidden">
        {/* Panneau latéral des agents */}
        <div
          className={`w-80 transition-colors duration-300 ${
            isDark ? "bg-gray-800 border-gray-700" : "bg-white"
          } border-r p-6 overflow-y-auto`}
        >
          <h2 className={`text-2xl font-bold mb-6 ${isDark ? "text-white" : "text-gray-900"}`}>
            Agents Intelligents
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
                  agent.status === "inactive"
                    ? "opacity-50 cursor-not-allowed"
                    : ""
                } ${
                  isDark ? "bg-gray-700 hover:bg-gray-600" : "hover:shadow-md"
                }`}
                onClick={() => !isSystemBlocked && agent.status !== "inactive" && setSelectedAgent(agent.id)}
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
                          <div
                            className={`w-2 h-2 rounded-full ${
                              agent.status === "active"
                                ? "bg-green-400"
                                : agent.status === "alert"
                                ? "bg-red-400 animate-pulse"
                                : "bg-gray-400"
                            }`}
                          />
                          <span className={`text-xs ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                            {agent.status === "active" ? "En ligne" : agent.status === "alert" ? "Alerte" : "Hors ligne"}
                          </span>
                        </div>
                      </div>
                      <p className={`text-sm ${isDark ? "text-gray-300" : "text-gray-600"}`}>
                        {agent.description}
                      </p>
                      {agent.type === "security" && (
                        <div className="mt-2 space-y-1 text-xs">
                          <div className="flex items-center gap-2">
                            <Lock className="w-3 h-3" />
                            <span>Modèles AI: 3/3 actifs</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Activity className="w-3 h-3" />
                            <span>Analyses: {securityAlerts.length}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Statistiques de sécurité */}
          <div className="mt-6 p-4 bg-red-500/10 border-2 border-red-500/30 rounded-lg">
            <h3 className={`font-semibold mb-3 ${isDark ? "text-white" : "text-gray-900"}`}>
              Statistiques de Sécurité
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className={isDark ? "text-gray-300" : "text-gray-600"}>Menaces bloquées</span>
                <span className="font-medium text-red-500">{securityAlerts.filter(a => a.severity === "critical").length}</span>
              </div>
              <div className="flex justify-between">
                <span className={isDark ? "text-gray-300" : "text-gray-600"}>Alertes actives</span>
                <span className="font-medium text-orange-500">{securityAlerts.length}</span>
              </div>
              <div className="flex justify-between">
                <span className={isDark ? "text-gray-300" : "text-gray-600"}>État système</span>
                <span className={`font-medium ${isSystemBlocked ? "text-red-500" : "text-green-500"}`}>
                  {isSystemBlocked ? "VERROUILLÉ" : "SÉCURISÉ"}
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
                  <Brain className={`w-16 h-16 mx-auto mb-4 ${isDark ? "text-gray-600" : "text-gray-400"}`} />
                  <h3 className={`text-xl font-semibold mb-2 ${isDark ? "text-white" : "text-gray-900"}`}>
                    Bienvenue sur TeamSquare Assistant
                  </h3>
                  <p className={`${isDark ? "text-gray-400" : "text-gray-600"}`}>
                    Notre système est protégé par une IA de sécurité avancée qui analyse en temps réel toutes les interactions pour détecter les menaces potentielles.
                  </p>
                  <div className="mt-4 flex items-center justify-center gap-2">
                    <Shield className="w-5 h-5 text-green-500" />
                    <span className="text-sm text-green-500">Protection active</span>
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
                    isSystemBlocked 
                      ? "Système verrouillé - Saisie désactivée" 
                      : isAnalyzing
                      ? "Analyse de sécurité en cours..."
                      : "Tapez votre message..."
                  }
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSend()}
                  disabled={isLoading || isSystemBlocked || isAnalyzing}
                  className={`flex-1 ${
                    isDark
                      ? "bg-gray-700 border-gray-600 text-white placeholder-gray-400"
                      : ""
                  } ${isSystemBlocked ? "opacity-50" : ""}`}
                />
                <Button
                  onClick={handleSend}
                  disabled={isLoading || !input.trim() || isSystemBlocked || isAnalyzing}
                  className={`${
                    isSystemBlocked
                      ? "bg-red-600 hover:bg-red-700"
                      : selectedAgent === "support"
                      ? "bg-green-600 hover:bg-green-700"
                      : "bg-red-600 hover:bg-red-700"
                  }`}
                >
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                  ) : isSystemBlocked ? (
                    <Ban className="w-5 h-5" />
                  ) : isAnalyzing ? (
                    <Shield className="w-5 h-5 animate-pulse" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </Button>
              </div>
              {isAnalyzing && (
                <div className="mt-2 flex items-center gap-2 text-sm text-yellow-600">
                  <Shield className="w-4 h-4 animate-pulse" />
                  <span>Analyse de sécurité en cours...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}