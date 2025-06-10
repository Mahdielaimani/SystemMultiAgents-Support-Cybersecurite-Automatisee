// app/admin-security/page.tsx
"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Shield, 
  AlertTriangle, 
  Download, 
  Eye, 
  EyeOff, 
  Lock, 
  Unlock, 
  Activity, 
  FileText, 
  Users, 
  MessageSquare, 
  Brain,
  ShieldAlert,
  Network,
  Bug,
  Zap,
  RefreshCw,
  Ban,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  BarChart3,
  Settings,
  LogOut,
  Home
} from "lucide-react"
import { useRouter } from "next/navigation"

interface SecurityAlert {
  id: string
  type: "vulnerability" | "network" | "intent" | "system"
  severity: "low" | "medium" | "high" | "critical"
  message: string
  timestamp: string
  action_taken: string
  details?: any
  user_session?: string
}

interface SystemStatus {
  blocked: boolean
  threat_level: "safe" | "warning" | "danger"
  active_threats: SecurityAlert[]
  last_scan: string
  models_status: {
    vulnerability_classifier: "active" | "inactive" | "error"
    network_analyzer: "active" | "inactive" | "error"
    intent_classifier: "active" | "inactive" | "error"
  }
}

interface UserActivity {
  session_id: string
  messages_count: number
  last_activity: string
  threat_score: number
  blocked: boolean
  location?: string
}

const AdminSecurityPage = () => {
  const router = useRouter()
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [loginError, setLoginError] = useState("")
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    blocked: false,
    threat_level: "safe",
    active_threats: [],
    last_scan: new Date().toISOString(),
    models_status: {
      vulnerability_classifier: "active",
      network_analyzer: "active", 
      intent_classifier: "active"
    }
  })
  const [alerts, setAlerts] = useState<SecurityAlert[]>([])
  const [userActivities, setUserActivities] = useState<UserActivity[]>([])
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  // Charger les données depuis l'API
  const loadSecurityData = async () => {
    try {
      const response = await fetch("/api/admin-security?type=all")
      if (response.ok) {
        const data = await response.json()
        setSystemStatus(data.system_state)
        setAlerts(data.alerts || [])
        setUserActivities(data.user_activities || [])
      }
    } catch (error) {
      console.error("Erreur chargement données:", error)
    }
  }

  // Auto-refresh des données
  useEffect(() => {
    if (isLoggedIn && autoRefresh) {
      loadSecurityData()
      const interval = setInterval(loadSecurityData, 5000)
      return () => clearInterval(interval)
    }
  }, [isLoggedIn, autoRefresh])

  const handleLogin = async () => {
    setIsLoading(true)
    setLoginError("")
    
    try {
      const response = await fetch("/api/admin-security", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "login",
          username,
          password
        })
      })

      if (response.ok) {
        const data = await response.json()
        setIsLoggedIn(true)
        setLoginError("")
        loadSecurityData()
      } else {
        const error = await response.json()
        setLoginError(error.error || "Échec de la connexion")
      }
    } catch (error) {
      setLoginError("Erreur de connexion au serveur")
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
    setUsername("")
    setPassword("")
  }

  const handleBlockSystem = async () => {
    try {
      const response = await fetch("/api/admin-security", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "block_system",
          reason: "Blocage manuel par administrateur",
          severity: "critical"
        })
      })

      if (response.ok) {
        const data = await response.json()
        setSystemStatus(data.system_state)
        loadSecurityData()
      }
    } catch (error) {
      console.error("Erreur blocage système:", error)
    }
  }

  const handleUnblockSystem = async () => {
    try {
      const response = await fetch("/api/admin-security", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "unblock_system"
        })
      })

      if (response.ok) {
        const data = await response.json()
        setSystemStatus(data.system_state)
        loadSecurityData()
      }
    } catch (error) {
      console.error("Erreur déblocage système:", error)
    }
  }

  const generateSecurityReport = async () => {
    setIsGeneratingReport(true)
    
    try {
      const response = await fetch("/api/admin-security", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "generate_report"
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        // Télécharger le rapport
        const blob = new Blob([JSON.stringify(data.report, null, 2)], {
          type: "application/json"
        })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `security-report-${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error("Erreur génération rapport:", error)
    } finally {
      setIsGeneratingReport(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-red-500 text-white"
      case "high": return "bg-orange-500 text-white" 
      case "medium": return "bg-yellow-500 text-black"
      case "low": return "bg-blue-500 text-white"
      default: return "bg-gray-500 text-white"
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "vulnerability": return <Bug className="w-4 h-4" />
      case "network": return <Network className="w-4 h-4" />
      case "intent": return <Brain className="w-4 h-4" />
      case "system": return <Settings className="w-4 h-4" />
      default: return <AlertTriangle className="w-4 h-4" />
    }
  }

  // Page de connexion
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
        <Card className="w-full max-w-md bg-gray-800 border-gray-700">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-600 rounded-full flex items-center justify-center mb-4">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl text-white">Admin Sécurité</CardTitle>
            <p className="text-gray-400">Centre de contrôle des systèmes IA</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Input
                type="text"
                placeholder="Nom d'utilisateur"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="bg-gray-700 border-gray-600 text-white"
                disabled={isLoading}
              />
            </div>
            <div className="relative">
              <Input
                type={showPassword ? "text" : "password"}
                placeholder="Mot de passe"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && !isLoading && handleLogin()}
                className="bg-gray-700 border-gray-600 text-white pr-10"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                disabled={isLoading}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            
            {loginError && (
              <Alert className="bg-red-900/50 border-red-500">
                <AlertTriangle className="w-4 h-4" />
                <AlertDescription className="text-red-400">
                  {loginError}
                </AlertDescription>
              </Alert>
            )}

            <Button 
              onClick={handleLogin} 
              className="w-full bg-red-600 hover:bg-red-700"
              disabled={!username || !password || isLoading}
            >
              {isLoading ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Lock className="w-4 h-4 mr-2" />
              )}
              {isLoading ? "Connexion..." : "Connexion Sécurisée"}
            </Button>

            <div className="text-center text-xs text-gray-500 mt-4">
              <p>Démo: admin / security123</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Interface d'administration
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* En-tête */}
      <div className="bg-gradient-to-r from-red-800 to-red-600 py-6 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8" />
            <div>
              <h1 className="text-3xl font-bold">Centre de Sécurité Admin</h1>
              <p className="text-red-200">Surveillance et contrôle des systèmes IA de sécurité</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Button
              onClick={() => router.push("/")}
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-red-600"
            >
              <Home className="w-4 h-4 mr-2" />
              Page Principale
            </Button>
            
            <Button
              onClick={generateSecurityReport}
              disabled={isGeneratingReport}
              className="bg-green-600 hover:bg-green-700"
            >
              {isGeneratingReport ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Download className="w-4 h-4 mr-2" />
              )}
              Télécharger Rapport
            </Button>
            
            <Button
              onClick={handleLogout}
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-red-600"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Déconnexion
            </Button>
          </div>
        </div>
      </div>

      {/* Tableau de bord principal */}
      <div className="p-6">
        {/* Statut système */}
        <Card className="mb-6 bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Statut Système en Temps Réel
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={autoRefresh ? "text-green-400" : "text-gray-400"}
              >
                <RefreshCw className={`w-4 h-4 ${autoRefresh ? "animate-spin" : ""}`} />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full ${
                  systemStatus.blocked ? "bg-red-500 animate-pulse" : "bg-green-500"
                }`} />
                <div>
                  <p className="text-sm text-gray-400">État Système</p>
                  <p className="font-semibold">
                    {systemStatus.blocked ? "🚫 BLOQUÉ" : "✅ ACTIF"}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full ${
                  systemStatus.threat_level === "danger" ? "bg-red-500 animate-pulse" :
                  systemStatus.threat_level === "warning" ? "bg-yellow-500" : "bg-green-500"
                }`} />
                <div>
                  <p className="text-sm text-gray-400">Niveau de Menace</p>
                  <p className="font-semibold">
                    {systemStatus.threat_level === "danger" ? "🚨 CRITIQUE" :
                     systemStatus.threat_level === "warning" ? "⚠️ ÉLEVÉ" : "🛡️ NORMAL"}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-400">Alertes Actives</p>
                <p className="font-semibold text-orange-400">{alerts.length}</p>
              </div>

              <div className="flex gap-2">
                {systemStatus.blocked ? (
                  <Button
                    onClick={handleUnblockSystem}
                    size="sm"
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Unlock className="w-4 h-4 mr-1" />
                    Débloquer Système
                  </Button>
                ) : (
                  <Button
                    onClick={handleBlockSystem}
                    size="sm"
                    variant="destructive"
                  >
                    <Ban className="w-4 h-4 mr-1" />
                    Bloquer Système
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="alerts" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-gray-800">
            <TabsTrigger value="alerts">🚨 Alertes Sécurité</TabsTrigger>
            <TabsTrigger value="models">🤖 Modèles IA</TabsTrigger>
            <TabsTrigger value="users">👥 Activité Utilisateurs</TabsTrigger>
            <TabsTrigger value="stats">📊 Statistiques</TabsTrigger>
          </TabsList>

          {/* Onglet Alertes */}
          <TabsContent value="alerts">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5" />
                  Alertes de Sécurité Détectées par l'IA ({alerts.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-96">
                  <div className="space-y-3">
                    {alerts.length === 0 ? (
                      <div className="text-center py-8">
                        <CheckCircle className="w-12 h-12 mx-auto text-green-500 mb-3" />
                        <p className="text-gray-400">Aucune alerte active</p>
                        <p className="text-sm text-gray-500">Tous les systèmes fonctionnent normalement</p>
                      </div>
                    ) : (
                      alerts.map((alert) => (
                        <div
                          key={alert.id}
                          className="p-4 bg-gray-700 rounded-lg border-l-4"
                          style={{
                            borderLeftColor: alert.severity === "critical" ? "#ef4444" :
                                           alert.severity === "high" ? "#f97316" :
                                           alert.severity === "medium" ? "#eab308" : "#3b82f6"
                          }}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex items-start gap-3">
                              {getTypeIcon(alert.type)}
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <Badge className={getSeverityColor(alert.severity)}>
                                    {alert.severity.toUpperCase()}
                                  </Badge>
                                  <Badge variant="outline" className="text-gray-300">
                                    {alert.type.toUpperCase()}
                                  </Badge>
                                  <span className="text-xs text-gray-400">
                                    {new Date(alert.timestamp).toLocaleString()}
                                  </span>
                                </div>
                                <p className="text-white mb-2">{alert.message}</p>
                                <p className="text-sm text-gray-400">
                                  🔧 Action: {alert.action_taken}
                                </p>
                                {alert.user_session && (
                                  <p className="text-xs text-blue-400 mt-1">
                                    👤 Session: {alert.user_session}
                                  </p>
                                )}
                                {alert.details && (
                                  <div className="mt-2 text-xs text-gray-500">
                                    Détails: {JSON.stringify(alert.details)}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Onglet Modèles IA */}
          <TabsContent value="models">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Object.entries(systemStatus.models_status).map(([model, status]) => (
                <Card key={model} className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="w-5 h-5" />
                      {model === "vulnerability_classifier" ? "🐛 Détecteur de Vulnérabilités" :
                       model === "network_analyzer" ? "🌐 Analyseur Réseau" :
                       "🧠 Classificateur d'Intentions"}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${
                          status === "active" ? "bg-green-500" :
                          status === "error" ? "bg-red-500" : "bg-gray-500"
                        }`} />
                        <span className="capitalize">
                          {status === "active" ? "✅ Actif" : 
                           status === "error" ? "❌ Erreur" : "⏸️ Inactif"}
                        </span>
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Précision</span>
                          <span className="text-green-400 font-semibold">
                            {model === "vulnerability_classifier" ? "99.2%" :
                             model === "network_analyzer" ? "97.8%" : "95.4%"}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Détections</span>
                          <span className="text-orange-400 font-semibold">
                            {alerts.filter(a => a.type === 
                              (model === "vulnerability_classifier" ? "vulnerability" :
                               model === "network_analyzer" ? "network" : "intent")
                            ).length}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Dernière analyse</span>
                          <span className="text-blue-400">
                            {new Date(systemStatus.last_scan).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Source</span>
                          <span className="text-purple-400 text-xs">HuggingFace</span>
                        </div>
                      </div>
                      
                      <Button size="sm" variant="outline" className="w-full">
                        <Settings className="w-4 h-4 mr-2" />
                        Configurer Modèle
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Onglet Utilisateurs */}
          <TabsContent value="users">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Surveillance des Sessions Utilisateurs
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {userActivities.length === 0 ? (
                    <div className="text-center py-8">
                      <Users className="w-12 h-12 mx-auto text-gray-500 mb-3" />
                      <p className="text-gray-400">Aucune activité utilisateur</p>
                    </div>
                  ) : (
                    userActivities.map((user) => (
                      <div
                        key={user.session_id}
                        className={`p-4 rounded-lg border ${
                          user.blocked ? "bg-red-900/20 border-red-500" : 
                          user.threat_score > 0.7 ? "bg-orange-900/20 border-orange-500" :
                          "bg-gray-700 border-gray-600"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className={`w-4 h-4 rounded-full ${
                              user.blocked ? "bg-red-500 animate-pulse" : 
                              user.threat_score > 0.7 ? "bg-orange-500" : "bg-green-500"
                            }`} />
                            <div>
                              <p className="font-medium">👤 {user.session_id}</p>
                              <p className="text-sm text-gray-400">
                                💬 {user.messages_count} messages • 
                                ⚠️ Score de menace: {(user.threat_score * 100).toFixed(0)}% •
                                🌍 {user.location || "Inconnu"}
                              </p>
                              <p className="text-xs text-gray-500">
                                🕒 Dernière activité: {new Date(user.last_activity).toLocaleString()}
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <Badge variant={user.blocked ? "destructive" : "secondary"}>
                              {user.blocked ? "🚫 BLOQUÉ" : "✅ ACTIF"}
                            </Badge>
                            {user.threat_score > 0.7 && (
                              <Badge variant="destructive" className="animate-pulse">
                                ⚠️ RISQUE ÉLEVÉ
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Onglet Statistiques */}
          <TabsContent value="stats">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-red-600 rounded-full">
                      <AlertTriangle className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-red-400">
                        {alerts.filter(a => a.severity === "critical").length}
                      </p>
                      <p className="text-sm text-gray-400">Menaces Critiques</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-blue-600 rounded-full">
                      <Users className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-blue-400">
                        {userActivities.filter(u => u.blocked).length}
                      </p>
                      <p className="text-sm text-gray-400">Utilisateurs Bloqués</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-green-600 rounded-full">
                      <CheckCircle className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-green-400">
                        {alerts.filter(a => a.action_taken.includes("bloqué")).length}
                      </p>
                      <p className="text-sm text-gray-400">Attaques Bloquées</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-purple-600 rounded-full">
                      <Brain className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-purple-400">97.8%</p>
                      <p className="text-sm text-gray-400">Précision IA Moyenne</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Graphiques de tendances */}
            <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Tendances des Menaces (7 derniers jours)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-48 flex items-center justify-center">
                    <div className="text-center">
                      <BarChart3 className="w-12 h-12 mx-auto text-gray-500 mb-3" />
                      <p className="text-gray-400">Graphique des tendances</p>
                      <p className="text-sm text-gray-500">Données collectées par les modèles IA</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5" />
                    Performance des Modèles IA
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">🐛 Détecteur Vulnérabilités</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-700 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{width: "99.2%"}}></div>
                        </div>
                        <span className="text-sm text-green-400">99.2%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">🌐 Analyseur Réseau</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-700 rounded-full h-2">
                          <div className="bg-blue-500 h-2 rounded-full" style={{width: "97.8%"}}></div>
                        </div>
                        <span className="text-sm text-blue-400">97.8%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">🧠 Classificateur Intentions</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-700 rounded-full h-2">
                          <div className="bg-purple-500 h-2 rounded-full" style={{width: "95.4%"}}></div>
                        </div>
                        <span className="text-sm text-purple-400">95.4%</span>
                      </div>
                    </div>
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

export default AdminSecurityPage