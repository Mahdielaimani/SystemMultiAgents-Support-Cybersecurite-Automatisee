"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Shield,
  MessageSquare,
  Scan,
  AlertTriangle,
  CheckCircle,
  Activity,
  FileText,
  Bot,
  Send,
  Loader2,
  Eye,
  Lock,
  Zap,
} from "lucide-react"

interface Message {
  id: string
  content: string
  sender: "user" | "support" | "security"
  timestamp: Date
  metadata?: any
}

interface ScanResult {
  scan_id: string
  target: string
  status: string
  vulnerabilities: number
  threats: boolean
  timestamp: string
}

export default function UnifiedSecurityDashboard() {
  const [activeTab, setActiveTab] = useState("chat")
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [scanTarget, setScanTarget] = useState("")
  const [scanResults, setScanResults] = useState<ScanResult[]>([])
  const [agentStats, setAgentStats] = useState({
    support: { queries: 0, sessions: 0, satisfaction: 95 },
    security: { scans: 0, threats: 0, vulnerabilities: 0 },
  })

  // Simulation de données en temps réel
  useEffect(() => {
    const interval = setInterval(() => {
      setAgentStats((prev) => ({
        support: {
          ...prev.support,
          queries: prev.support.queries + Math.floor(Math.random() * 3),
          sessions: prev.support.sessions + Math.floor(Math.random() * 2),
        },
        security: {
          ...prev.security,
          scans: prev.security.scans + Math.floor(Math.random() * 2),
        },
      }))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const sendMessage = async (agentType: "support" | "security") => {
    if (!inputValue.trim()) return

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
      // Simuler l'appel API selon l'agent
      const endpoint = agentType === "support" ? "/api/agentic/chat" : "/api/security/analyze"

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: inputValue,
          agent_type: agentType,
        }),
      })

      const data = await response.json()

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response || getSimulatedResponse(inputValue, agentType),
        sender: agentType,
        timestamp: new Date(),
        metadata: data.metadata,
      }

      setMessages((prev) => [...prev, agentMessage])
    } catch (error) {
      console.error("Erreur:", error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: getSimulatedResponse(inputValue, agentType),
        sender: agentType,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const getSimulatedResponse = (query: string, agentType: "support" | "security") => {
    if (agentType === "support") {
      if (query.toLowerCase().includes("prix") || query.toLowerCase().includes("tarif")) {
        return "Nos tarifs TeamSquare : Starter 9€/mois, Professional 19€/mois, Enterprise sur devis. Lequel vous intéresse ?"
      }
      return "Bonjour ! Je suis l'assistant TeamSquare. Comment puis-je vous aider avec notre plateforme de collaboration ?"
    } else {
      if (query.toLowerCase().includes("scan") || query.toLowerCase().includes("sécurité")) {
        return "🔒 Analyse de sécurité en cours... Je détecte quelques vulnérabilités mineures. Voulez-vous un rapport détaillé ?"
      }
      return "🛡️ Agent de cybersécurité à votre service. Je peux analyser des URLs, détecter des vulnérabilités et surveiller le trafic réseau."
    }
  }

  const performSecurityScan = async () => {
    if (!scanTarget.trim()) return

    setIsLoading(true)

    try {
      // Simuler un scan de sécurité
      await new Promise((resolve) => setTimeout(resolve, 3000))

      const newScan: ScanResult = {
        scan_id: `scan_${Date.now()}`,
        target: scanTarget,
        status: "completed",
        vulnerabilities: Math.floor(Math.random() * 5),
        threats: Math.random() > 0.7,
        timestamp: new Date().toISOString(),
      }

      setScanResults((prev) => [newScan, ...prev.slice(0, 4)])
      setScanTarget("")

      setAgentStats((prev) => ({
        ...prev,
        security: {
          ...prev.security,
          scans: prev.security.scans + 1,
          vulnerabilities: prev.security.vulnerabilities + newScan.vulnerabilities,
          threats: prev.security.threats + (newScan.threats ? 1 : 0),
        },
      }))
    } catch (error) {
      console.error("Erreur scan:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            NextGen Security Hub
          </h1>
          <p className="text-lg text-muted-foreground">Plateforme unifiée d'assistance et de cybersécurité</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100">Requêtes Support</p>
                  <p className="text-2xl font-bold">{agentStats.support.queries}</p>
                </div>
                <MessageSquare className="h-8 w-8 text-blue-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100">Scans Sécurité</p>
                  <p className="text-2xl font-bold">{agentStats.security.scans}</p>
                </div>
                <Shield className="h-8 w-8 text-purple-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-orange-500 to-red-500 text-white">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100">Vulnérabilités</p>
                  <p className="text-2xl font-bold">{agentStats.security.vulnerabilities}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-orange-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100">Satisfaction</p>
                  <p className="text-2xl font-bold">{agentStats.support.satisfaction}%</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-200" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Interface */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Chat Unifié
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Sécurité
            </TabsTrigger>
            <TabsTrigger value="monitoring" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Monitoring
            </TabsTrigger>
            <TabsTrigger value="reports" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Rapports
            </TabsTrigger>
          </TabsList>

          {/* Chat Unifié */}
          <TabsContent value="chat" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Support Agent */}
              <Card className="h-[600px] flex flex-col">
                <CardHeader className="bg-blue-50 dark:bg-blue-900/20">
                  <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
                    <Bot className="h-5 w-5" />
                    Assistant TeamSquare
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col p-0">
                  <ScrollArea className="flex-1 p-4">
                    <div className="space-y-4">
                      {messages
                        .filter((m) => m.sender === "user" || m.sender === "support")
                        .map((message) => (
                          <div
                            key={message.id}
                            className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                          >
                            <div
                              className={`max-w-[80%] rounded-lg p-3 ${
                                message.sender === "user" ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"
                              }`}
                            >
                              <p className="text-sm">{message.content}</p>
                              <p className="text-xs opacity-70 mt-1">{message.timestamp.toLocaleTimeString()}</p>
                            </div>
                          </div>
                        ))}
                    </div>
                  </ScrollArea>
                  <div className="p-4 border-t">
                    <div className="flex gap-2">
                      <Input
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Posez votre question sur TeamSquare..."
                        onKeyPress={(e) => e.key === "Enter" && sendMessage("support")}
                      />
                      <Button
                        onClick={() => sendMessage("support")}
                        disabled={isLoading}
                        className="bg-blue-500 hover:bg-blue-600"
                      >
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Security Agent */}
              <Card className="h-[600px] flex flex-col">
                <CardHeader className="bg-purple-50 dark:bg-purple-900/20">
                  <CardTitle className="flex items-center gap-2 text-purple-700 dark:text-purple-300">
                    <Shield className="h-5 w-5" />
                    Agent Cybersécurité
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col p-0">
                  <ScrollArea className="flex-1 p-4">
                    <div className="space-y-4">
                      {messages
                        .filter((m) => m.sender === "user" || m.sender === "security")
                        .map((message) => (
                          <div
                            key={message.id}
                            className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                          >
                            <div
                              className={`max-w-[80%] rounded-lg p-3 ${
                                message.sender === "user" ? "bg-purple-500 text-white" : "bg-gray-100 dark:bg-gray-800"
                              }`}
                            >
                              <p className="text-sm">{message.content}</p>
                              <p className="text-xs opacity-70 mt-1">{message.timestamp.toLocaleTimeString()}</p>
                            </div>
                          </div>
                        ))}
                    </div>
                  </ScrollArea>
                  <div className="p-4 border-t">
                    <div className="flex gap-2">
                      <Input
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Demandez une analyse de sécurité..."
                        onKeyPress={(e) => e.key === "Enter" && sendMessage("security")}
                      />
                      <Button
                        onClick={() => sendMessage("security")}
                        disabled={isLoading}
                        className="bg-purple-500 hover:bg-purple-600"
                      >
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Quick Scan */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Scan className="h-5 w-5" />
                    Scan Rapide
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      value={scanTarget}
                      onChange={(e) => setScanTarget(e.target.value)}
                      placeholder="https://example.com"
                    />
                    <Button onClick={performSecurityScan} disabled={isLoading} className="bg-red-500 hover:bg-red-600">
                      {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Scan className="h-4 w-4" />}
                    </Button>
                  </div>

                  {isLoading && (
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">Scan en cours...</p>
                      <Progress value={33} className="w-full" />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Recent Scans */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="h-5 w-5" />
                    Scans Récents
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[200px]">
                    <div className="space-y-2">
                      {scanResults.map((scan) => (
                        <div key={scan.scan_id} className="flex items-center justify-between p-2 border rounded">
                          <div>
                            <p className="font-medium text-sm">{scan.target}</p>
                            <p className="text-xs text-muted-foreground">{new Date(scan.timestamp).toLocaleString()}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant={scan.threats ? "destructive" : "secondary"}>
                              {scan.vulnerabilities} vulns
                            </Badge>
                            {scan.threats && <AlertTriangle className="h-4 w-4 text-red-500" />}
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>

            {/* Security Alerts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Alertes Sécurité
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <Alert>
                    <Lock className="h-4 w-4" />
                    <AlertDescription>
                      Nouvelle vulnérabilité détectée sur example.com - En-tête CSP manquant
                    </AlertDescription>
                  </Alert>
                  <Alert>
                    <Zap className="h-4 w-4" />
                    <AlertDescription>Trafic réseau suspect détecté - Investigation en cours</AlertDescription>
                  </Alert>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Monitoring Tab */}
          <TabsContent value="monitoring" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Activité Support</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Sessions actives</span>
                      <span className="font-medium">{agentStats.support.sessions}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Temps de réponse</span>
                      <span className="font-medium">1.2s</span>
                    </div>
                    <Progress value={85} className="w-full" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Sécurité Réseau</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Menaces bloquées</span>
                      <span className="font-medium">{agentStats.security.threats}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Statut</span>
                      <Badge variant="secondary">Protégé</Badge>
                    </div>
                    <Progress value={95} className="w-full" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Performance Système</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">CPU</span>
                      <span className="font-medium">45%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Mémoire</span>
                      <span className="font-medium">62%</span>
                    </div>
                    <Progress value={45} className="w-full" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Rapport de Sécurité Hebdomadaire</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded">
                        <p className="text-2xl font-bold text-green-600">{agentStats.security.scans}</p>
                        <p className="text-sm text-green-700 dark:text-green-300">Scans effectués</p>
                      </div>
                      <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded">
                        <p className="text-2xl font-bold text-red-600">{agentStats.security.vulnerabilities}</p>
                        <p className="text-sm text-red-700 dark:text-red-300">Vulnérabilités</p>
                      </div>
                    </div>
                    <Button className="w-full">
                      <FileText className="h-4 w-4 mr-2" />
                      Télécharger le rapport complet
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Analyse Support Client</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded">
                        <p className="text-2xl font-bold text-blue-600">{agentStats.support.queries}</p>
                        <p className="text-sm text-blue-700 dark:text-blue-300">Requêtes traitées</p>
                      </div>
                      <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded">
                        <p className="text-2xl font-bold text-purple-600">{agentStats.support.satisfaction}%</p>
                        <p className="text-sm text-purple-700 dark:text-purple-300">Satisfaction</p>
                      </div>
                    </div>
                    <Button className="w-full" variant="outline">
                      <FileText className="h-4 w-4 mr-2" />
                      Exporter les métriques
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
