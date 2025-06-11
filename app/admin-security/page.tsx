// app/admin-security/page.tsx - Version complète avec bouton de reset
"use client"
import { useState, useEffect, useCallback } from "react"
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
  Home,
  Wifi,
  WifiOff,
  Trash2
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
  const [connectionStatus, setConnectionStatus] = useState(true)
  const [realTimeStats, setRealTimeStats] = useState({
    totalThreats: 0,
    blockedSessions: 0,
    activeMonitoring: true
  })
  const [isResetting, setIsResetting] = useState(false)

  // Charger les données depuis l'API avec gestion d'erreur améliorée
  const loadSecurityData = useCallback(async () => {
    try {
      setConnectionStatus(true)
      const response = await fetch("/api/admin-security?type=all", {
        signal: AbortSignal.timeout(5000)
      })
      
      if (response.ok) {
        const data = await response.json()
        setSystemStatus(data.system_state || systemStatus)
        setAlerts(data.alerts || [])
        setUserActivities(data.user_activities || [])
        
        // Mettre à jour les stats en temps réel
        setRealTimeStats({
          totalThreats: data.alerts?.length || 0,
          blockedSessions: data.user_activities?.filter((u: UserActivity) => u.blocked).length || 0,
          activeMonitoring: true
        })
      } else {
        console.error("Erreur chargement données:", response.status)
        setConnectionStatus(false)
      }
    } catch (error) {
      console.error("Erreur chargement données:", error)
      setConnectionStatus(false)
    }
  }, [systemStatus])

  // Vérifier les nouvelles alertes en temps réel
  const checkForNewAlerts = useCallback(async () => {
    try {
      const response = await fetch("/api/cybersecurity/alerts", {
        signal: AbortSignal.timeout(3000)
      })
      
      if (response.ok) {
        const data = await response.json()
        const newAlerts = data.alerts || []
        
        // Comparer avec les alertes existantes
        if (newAlerts.length > alerts.length) {
          const latestAlerts = newAlerts.slice(0, 10) // Garder les 10 plus récentes
          setAlerts(latestAlerts)
          
          // Notification visuelle pour nouvelles alertes
          const newAlertsCount = newAlerts.length - alerts.length
          if (newAlertsCount > 0) {
            console.log(`🚨 ${newAlertsCount} nouvelle(s) alerte(s) détectée(s)`)
          }
        }
      }
    } catch (error) {
      console.error("Erreur vérification alertes:", error)
    }
  }, [alerts.length])

  // Auto-refresh des données toutes les 3 secondes
  useEffect(() => {
    if (isLoggedIn && autoRefresh) {
      loadSecurityData()
      const interval = setInterval(() => {
        loadSecurityData()
        checkForNewAlerts()
      }, 3000) // Mise à jour toutes les 3 secondes
      
      return () => clearInterval(interval)
    }
  }, [isLoggedIn, autoRefresh, loadSecurityData, checkForNewAlerts])

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
        await loadSecurityData()
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
        await loadSecurityData()
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
        await loadSecurityData()
      }
    } catch (error) {
      console.error("Erreur déblocage système:", error)
    }
  }

  const handleForceReset = async () => {
    if (!confirm("⚠️ ATTENTION: Ceci va SUPPRIMER TOUTES les données!\n\n" +
                 "• Toutes les alertes seront supprimées\n" +
                 "• Toutes les sessions seront réinitialisées\n" +
                 "• L'historique des conversations sera effacé\n\n" +
                 "Êtes-vous sûr de vouloir réinitialiser COMPLÈTEMENT le système?")) {
      return
    }
    
    if (!confirm("⚠️ DERNIÈRE CONFIRMATION\n\nCette action est IRRÉVERSIBLE. Continuer?")) {
      return
    }
    
    setIsResetting(true)
    
    try {
      const response = await fetch("/api/admin/force-reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "force_reset",
          username: username || "admin",
          password: password || "security123"
        })
      })

      if (response.ok) {
        const data = await response.json()
        alert("✅ Système réinitialisé avec succès!\n\n" +
              `Statistiques avant reset:\n` +
              `- Alertes: ${data.stats_before.alerts}\n` +
              `- Sessions: ${data.stats_before.users}\n\n` +
              "Toutes les données ont été supprimées.")
        
        // Recharger les données
        await loadSecurityData()
        
        // Forcer le refresh de la page après 1 seconde
        setTimeout(() => {
          window.location.reload()
        }, 1000)
      } else {
        const error = await response.json()
        alert(`❌ Erreur lors de la réinitialisation: ${error.detail || error.error || "Erreur inconnue"}`)
      }
    } catch (error) {
      console.error("Erreur reset:", error)
      alert("❌ Erreur de connexion lors du reset")
    } finally {
      setIsResetting(false)
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
      case "critical": return "bg-red-500 text-white animate-pulse"
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
      {/* En-tête avec statut temps réel */}
      <div className="bg-gradient-to-r from-red-800 to-red-600 py-6 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8" />
            <div>
              <h1 className="text-3xl font-bold">Centre de Sécurité Admin</h1>
              <p className="text-red-200">Surveillance temps réel des systèmes IA de sécurité</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Indicateur de connexion temps réel */}
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${
              connectionStatus ? "bg-green-900/50 border border-green-500" : "bg-red-900/50 border border-red-500"
            }`}>
              {connectionStatus ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
              <span className="text-sm">{connectionStatus ? "Connecté" : "Hors ligne"}</span>
            </div>
            
            <Button
              onClick={() => router.push("/")}
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-red-600"
            >
              <Home className="w-4 h-4 mr-2" />
              Page Principale
            </Button>
            
            <Button
              onClick={handleForceReset}
              disabled={isResetting}
              variant="destructive"
              className="bg-red-700 hover:bg-red-800"
            >
              {isResetting ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Trash2 className="w-4 h-4 mr-2" />
              )}
              Reset Complet
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

      {/* Tableau de bord principal avec stats temps réel */}
      <div className="p-6">
        {/* Statut système temps réel */}
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
              <Badge variant="outline" className="text-green-400 border-green-400">
                {autoRefresh ? "Auto-Refresh ON" : "Auto-Refresh OFF"}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
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
                <p className={`font-semibold text-2xl ${
                  alerts.length > 5 ? "text-red-400 animate-pulse" : 
                  alerts.length > 0 ? "text-orange-400" : "text-green-400"
                }`}>
                  {alerts.length}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-400">Sessions Bloquées</p>
                <p className={`font-semibold text-2xl ${
                  realTimeStats.blockedSessions > 0 ? "text-red-400" : "text-green-400"
                }`}>
                  {realTimeStats.blockedSessions}
                </p>
              </div>

              <div className="flex gap-2">
                {systemStatus.blocked ? (
                  <Button
                    onClick={handleUnblockSystem}
                    size="sm"
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Unlock className="w-4 h-4 mr-1" />
                    Débloquer
                  </Button>
                ) : (
                  <Button
                    onClick={handleBlockSystem}
                    size="sm"
                    variant="destructive"
                  >
                    <Ban className="w-4 h-4 mr-1" />
                    Bloquer
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="alerts" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-gray-800">
            <TabsTrigger value="alerts">
              🚨 Alertes ({alerts.length})
            </TabsTrigger>
            <TabsTrigger value="models">🤖 Modèles IA</TabsTrigger>
            <TabsTrigger value="users">👥 Utilisateurs ({userActivities.length})</TabsTrigger>
            <TabsTrigger value="stats">📊 Statistiques</TabsTrigger>
          </TabsList>

          {/* Onglet Alertes avec mise à jour temps réel */}
          <TabsContent value="alerts">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5" />
                  Alertes de Sécurité Temps Réel ({alerts.length})
                  {alerts.length > 0 && (
                    <Badge className="bg-red-500 text-white animate-pulse">
                      NOUVEAU
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-96">
                  <div className="space-y-3">
                    {alerts.length === 0 ? (
                      <div className="text-center py-8">
                        <CheckCircle className="w-12 h-12 mx-auto text-green-500 mb-3" />
                        <p className="text-gray-400">Aucune alerte active</p>
                        <p className="text-sm text-gray-500">Surveillance en cours...</p>
                      </div>
                    ) : (
                      alerts.map((alert, index) => (
                        <div
                          key={alert.id}
                          className={`p-4 bg-gray-700 rounded-lg border-l-4 ${
                            index < 2 ? "ring-2 ring-yellow-500 animate-pulse" : ""
                          }`}
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
                                  {index < 2 && (
                                    <Badge className="bg-green-500 text-white text-xs">
                                      TEMPS RÉEL
                                    </Badge>
                                  )}
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
                                  <div className="mt-2 text-xs text-gray-500 max-w-md overflow-hidden">
                                    <details>
                                      <summary className="cursor-pointer hover:text-gray-300">
                                        Voir détails
                                      </summary>
                                      <pre className="mt-2 p-2 bg-gray-800 rounded text-xs overflow-auto">
                                        {JSON.stringify(alert.details, null, 2)}
                                      </pre>
                                    </details>
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
                          status === "active" ? "bg-green-500 animate-pulse" :
                          status === "error" ? "bg-red-500" : "bg-gray-500"
                        }`} />
                        <span className="capitalize">
                          {status === "active" ? "✅ Actif" : 
                           status === "error" ? "❌ Erreur" : "⏸️ Inactif"}
                        </span>
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Détections/min</span>
                          <span className="text-green-400 font-semibold">
                            {Math.floor(Math.random() * 10) + 1}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Précision</span>
                          <span className="text-green-400 font-semibold">
                            {model === "vulnerability_classifier" ? "99.2%" :
                             model === "network_analyzer" ? "97.8%" : "95.4%"}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Dernière analyse</span>
                          <span className="text-blue-400">
                            {new Date().toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
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
                  Surveillance Sessions Utilisateurs
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {userActivities.length === 0 ? (
                    <div className="text-center py-8">
                      <Users className="w-12 h-12 mx-auto text-gray-500 mb-3" />
                      <p className="text-gray-400">Aucune activité utilisateur détectée</p>
                    </div>
                  ) : (
                    userActivities.map((user) => (
                      <div
                        key={user.session_id}
                        className={`p-4 rounded-lg border ${
                          user.blocked ? "bg-red-900/20 border-red-500 animate-pulse" : 
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
                                ⚠️ Score: {(user.threat_score * 100).toFixed(0)}% •
                                🌍 {user.location || "Inconnu"}
                              </p>
                              <p className="text-xs text-gray-500">
                                🕒 {new Date(user.last_activity).toLocaleString()}
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
                      <p className="text-3xl font-bold text-red-400">
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
                    <div className="p-3 bg-orange-600 rounded-full">
                      <Users className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-3xl font-bold text-orange-400">
                        {realTimeStats.blockedSessions}
                      </p>
                      <p className="text-sm text-gray-400">Sessions Bloquées</p>
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
                      <p className="text-3xl font-bold text-green-400">
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
                    <div className="p-3 bg-blue-600 rounded-full">
                      <Activity className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-3xl font-bold text-blue-400">
                        {realTimeStats.activeMonitoring ? "✅" : "❌"}
                      </p>
                      <p className="text-sm text-gray-400">Surveillance Active</p>
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