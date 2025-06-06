"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Shield, AlertTriangle, Activity, Globe, Zap, AlertCircle, FileCode } from "lucide-react"

interface RobotState {
  isScanning: boolean
  currentPage: string
  progress: number
  vulnerabilities: any[]
  attacks: any[]
  eyeColor: string
  mood: "happy" | "scanning" | "alert" | "sleeping" | "defending"
}

export function RobotGuardianInterface() {
  const [robotState, setRobotState] = useState<RobotState>({
    isScanning: false,
    currentPage: "",
    progress: 0,
    vulnerabilities: [],
    attacks: [],
    eyeColor: "#00FFFF",
    mood: "happy",
  })

  const [activeTab, setActiveTab] = useState("dashboard")
  const [alertVisible, setAlertVisible] = useState(false)
  const [alertMessage, setAlertMessage] = useState("")
  const [alertSeverity, setAlertSeverity] = useState<"low" | "medium" | "high" | "critical">("medium")

  // Simuler le scan de la plateforme
  const startScan = () => {
    if (robotState.isScanning) return

    setRobotState((prev) => ({
      ...prev,
      isScanning: true,
      progress: 0,
      mood: "scanning",
      eyeColor: "#FFD700",
    }))

    // Simuler la progression du scan
    const interval = setInterval(() => {
      setRobotState((prev) => {
        if (prev.progress >= 100) {
          clearInterval(interval)
          return {
            ...prev,
            isScanning: false,
            progress: 100,
            mood: "happy",
            eyeColor: "#00FFFF",
          }
        }

        // Simuler la découverte de pages
        const pages = [
          "http://localhost:3000/",
          "http://localhost:3000/api/chat",
          "http://localhost:3000/dashboard",
          "http://localhost:3000/settings",
          "http://localhost:3000/profile",
        ]

        const currentPageIndex = Math.floor((prev.progress / 100) * pages.length)
        const currentPage = pages[Math.min(currentPageIndex, pages.length - 1)]

        // Simuler la découverte de vulnérabilités
        if (prev.progress > 30 && prev.progress < 35) {
          const newVuln = {
            id: `vuln-${Date.now()}`,
            type: "XSS Potentiel",
            url: "http://localhost:3000/api/chat",
            description: "L'API de chat pourrait être vulnérable aux attaques XSS",
            severity: "high",
            timestamp: new Date().toISOString(),
          }

          // Afficher une alerte
          setAlertMessage("⚠️ Vulnérabilité XSS détectée dans l'API de chat!")
          setAlertSeverity("high")
          setAlertVisible(true)

          // Masquer l'alerte après 5 secondes
          setTimeout(() => setAlertVisible(false), 5000)

          return {
            ...prev,
            progress: prev.progress + 2,
            currentPage,
            vulnerabilities: [...prev.vulnerabilities, newVuln],
            mood: "alert",
            eyeColor: "#FF0000",
          }
        }

        // Simuler une attaque
        if (prev.progress > 70 && prev.progress < 75) {
          const newAttack = {
            id: `attack-${Date.now()}`,
            type: "Brute Force",
            source: "192.168.1.100",
            description: "Tentative de connexion répétée",
            severity: "medium",
            status: "blocked",
            timestamp: new Date().toISOString(),
          }

          // Afficher une alerte
          setAlertMessage("🚨 Attaque Brute Force détectée et bloquée!")
          setAlertSeverity("medium")
          setAlertVisible(true)

          // Masquer l'alerte après 5 secondes
          setTimeout(() => setAlertVisible(false), 5000)

          return {
            ...prev,
            progress: prev.progress + 2,
            currentPage,
            attacks: [...prev.attacks, newAttack],
            mood: "defending",
            eyeColor: "#FF0000",
          }
        }

        return {
          ...prev,
          progress: prev.progress + 2,
          currentPage,
          mood: prev.progress % 20 === 0 ? "scanning" : "happy",
          eyeColor: prev.progress % 20 === 0 ? "#FFD700" : "#00FFFF",
        }
      })
    }, 300)
  }

  // Simuler une attaque
  const simulateAttack = () => {
    const attackTypes = [
      {
        type: "SQL Injection",
        description: "Tentative d'injection SQL sur l'API",
        severity: "critical",
      },
      {
        type: "XSS",
        description: "Tentative d'injection de script dans le chat",
        severity: "high",
      },
    ]

    const attack = attackTypes[Math.floor(Math.random() * attackTypes.length)]

    const newAttack = {
      id: `attack-${Date.now()}`,
      type: attack.type,
      source: `192.168.1.${Math.floor(Math.random() * 255)}`,
      description: attack.description,
      severity: attack.severity,
      status: "blocked",
      timestamp: new Date().toISOString(),
    }

    setRobotState((prev) => ({
      ...prev,
      attacks: [...prev.attacks, newAttack],
      mood: "defending",
      eyeColor: "#FF0000",
    }))

    // Afficher une alerte
    setAlertMessage(`🚨 Attaque ${attack.type} détectée et bloquée!`)
    setAlertSeverity(attack.severity as any)
    setAlertVisible(true)

    // Masquer l'alerte après 5 secondes
    setTimeout(() => {
      setAlertVisible(false)
      setRobotState((prev) => ({
        ...prev,
        mood: "happy",
        eyeColor: "#00FFFF",
      }))
    }, 5000)
  }

  // Rendu du robot
  const renderRobot = () => {
    return (
      <div className="relative w-32 h-40 mx-auto">
        {/* Corps du robot */}
        <div className="w-24 h-32 bg-gradient-to-b from-gray-300 to-gray-400 rounded-2xl shadow-lg mx-auto">
          {/* Tête */}
          <div className="w-20 h-20 bg-gradient-to-b from-gray-200 to-gray-300 rounded-xl mx-auto -mt-4 relative">
            {/* Écran/Visage */}
            <div className="w-16 h-12 bg-gray-900 rounded-lg mx-auto mt-2 flex items-center justify-center">
              {/* Yeux */}
              <div className="flex gap-2">
                <div
                  className={`w-4 h-4 rounded-full ${
                    robotState.mood === "scanning"
                      ? "animate-pulse"
                      : robotState.mood === "alert"
                        ? "animate-bounce"
                        : robotState.mood === "defending"
                          ? "animate-ping"
                          : ""
                  }`}
                  style={{ backgroundColor: robotState.eyeColor }}
                />
                <div
                  className={`w-4 h-4 rounded-full ${
                    robotState.mood === "scanning"
                      ? "animate-pulse"
                      : robotState.mood === "alert"
                        ? "animate-bounce"
                        : robotState.mood === "defending"
                          ? "animate-ping"
                          : ""
                  }`}
                  style={{ backgroundColor: robotState.eyeColor }}
                />
              </div>
            </div>

            {/* Bouche */}
            <div
              className={`w-6 h-1 rounded-full mx-auto mt-2 ${
                robotState.mood === "alert" || robotState.mood === "defending" ? "bg-red-400" : "bg-cyan-400"
              }`}
            />
          </div>

          {/* Bras */}
          <div className="absolute -left-4 top-8 w-4 h-12 bg-gray-300 rounded-full" />
          <div className="absolute -right-4 top-8 w-4 h-12 bg-gray-300 rounded-full" />
        </div>

        {/* Effets de scan */}
        {robotState.isScanning && (
          <div className="absolute -inset-4">
            <div
              className="w-full h-full border-2 rounded-full animate-ping"
              style={{ borderColor: robotState.eyeColor }}
            />
          </div>
        )}

        {/* Texte d'état */}
        {robotState.currentPage && (
          <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs whitespace-nowrap">
            {robotState.isScanning ? `🔍 Scan: ${robotState.currentPage.split("/").pop() || "Accueil"}` : ""}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* En-tête */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              🤖 Robot Guardian Cybersécurité
            </h1>
            <p className="text-gray-400">Surveillance autonome de la plateforme NextGen AI Assistant</p>
          </div>

          <div className="flex items-center gap-2">
            <Button onClick={startScan} disabled={robotState.isScanning} className="bg-green-600 hover:bg-green-700">
              <Zap className="w-4 h-4 mr-2" />
              Scanner la Plateforme
            </Button>

            <Button onClick={simulateAttack} variant="outline">
              <Shield className="w-4 h-4 mr-2" />
              Simuler Attaque
            </Button>
          </div>
        </div>
      </div>

      {/* Alerte */}
      {alertVisible && (
        <Alert
          className={`mb-4 ${
            alertSeverity === "critical"
              ? "bg-red-900/20 border-red-800"
              : alertSeverity === "high"
                ? "bg-orange-900/20 border-orange-800"
                : "bg-yellow-900/20 border-yellow-800"
          }`}
        >
          <AlertCircle className="h-4 w-4" />
          <AlertTitle className="flex items-center gap-2">
            {alertSeverity === "critical" ? "ALERTE CRITIQUE" : "Alerte de sécurité"}
            <Badge variant={alertSeverity === "critical" || alertSeverity === "high" ? "destructive" : "default"}>
              {alertSeverity.toUpperCase()}
            </Badge>
          </AlertTitle>
          <AlertDescription>{alertMessage}</AlertDescription>
        </Alert>
      )}

      {/* Barre de progression */}
      {robotState.isScanning && (
        <div className="mb-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span>Scan en cours...</span>
            <span>{robotState.progress}%</span>
          </div>
          <Progress value={robotState.progress} className="h-2" />
        </div>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="grid grid-cols-3 mb-4">
          <TabsTrigger value="dashboard" className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="vulnerabilities" className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Vulnérabilités
          </TabsTrigger>
          <TabsTrigger value="attacks" className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Attaques
          </TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="flex-1 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Robot */}
            <Card className="md:col-span-2 bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Activity className="w-4 h-4" />
                  Robot Guardian en Action
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center py-8">
                {renderRobot()}

                <div className="mt-8 text-center">
                  <p className="text-sm text-gray-400">
                    {robotState.isScanning
                      ? "Robot en train de scanner la plateforme..."
                      : "Robot en attente de mission"}
                  </p>

                  <div className="mt-4 flex justify-center gap-2">
                    <Badge variant="outline">{robotState.vulnerabilities.length} Vulnérabilités</Badge>
                    <Badge variant="outline">{robotState.attacks.length} Attaques bloquées</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Statistiques */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Globe className="w-4 h-4" />
                  Plateforme NextGen
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">URL</span>
                    <span className="text-sm font-medium">localhost:3000</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Statut</span>
                    <Badge variant="outline" className="bg-green-900/20 text-green-400 border-green-800">
                      En ligne
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Niveau de sécurité</span>
                    <Badge variant={robotState.vulnerabilities.length > 0 ? "destructive" : "default"}>
                      {robotState.vulnerabilities.length > 0 ? "À risque" : "Sécurisé"}
                    </Badge>
                  </div>
                </div>

                <div className="pt-2 space-y-2">
                  <h3 className="text-sm font-medium">Pages surveillées</h3>
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center gap-2">
                      <FileCode className="w-3 h-3" />
                      <span>Accueil (localhost:3000)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <FileCode className="w-3 h-3" />
                      <span>API Chat (/api/chat)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <FileCode className="w-3 h-3" />
                      <span>Dashboard (/dashboard)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <FileCode className="w-3 h-3" />
                      <span>Paramètres (/settings)</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Activité récente */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm">
                <Activity className="w-4 h-4" />
                Activité Récente
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {[...robotState.attacks, ...robotState.vulnerabilities]
                  .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
                  .slice(0, 5)
                  .map((item, index) => {
                    const isAttack = "status" in item
                    return (
                      <div key={index} className="flex items-center justify-between bg-gray-800 p-2 rounded">
                        <div>
                          <p className="text-sm font-medium flex items-center gap-2">
                            {isAttack ? (
                              <Shield className="w-4 h-4 text-red-400" />
                            ) : (
                              <AlertTriangle className="w-4 h-4 text-yellow-400" />
                            )}
                            {isAttack ? `Attaque ${item.type}` : `Vulnérabilité ${item.type}`}
                          </p>
                          <p className="text-xs text-gray-400">{new Date(item.timestamp).toLocaleTimeString()}</p>
                        </div>
                        <Badge
                          variant={item.severity === "critical" || item.severity === "high" ? "destructive" : "default"}
                        >
                          {isAttack ? "Bloquée" : "Détectée"}
                        </Badge>
                      </div>
                    )
                  })}

                {robotState.attacks.length === 0 && robotState.vulnerabilities.length === 0 && (
                  <div className="text-center py-4 text-gray-400">
                    <Shield className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Aucune activité récente</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Vulnerabilities Tab */}
        <TabsContent value="vulnerabilities" className="flex-1">
          <Card className="bg-gray-900 border-gray-800 h-full">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Vulnérabilités Détectées
              </CardTitle>
            </CardHeader>
            <CardContent className="h-[calc(100%-60px)] overflow-auto">
              <div className="space-y-4">
                {robotState.vulnerabilities.length > 0 ? (
                  robotState.vulnerabilities.map((vuln, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border ${
                        vuln.severity === "critical"
                          ? "bg-red-900/20 border-red-800"
                          : vuln.severity === "high"
                            ? "bg-orange-900/20 border-orange-800"
                            : "bg-yellow-900/20 border-yellow-800"
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="flex items-center gap-2">
                            <Badge
                              variant={
                                vuln.severity === "critical" || vuln.severity === "high" ? "destructive" : "default"
                              }
                            >
                              {vuln.severity.toUpperCase()}
                            </Badge>
                            <h3 className="font-medium">{vuln.type}</h3>
                          </div>
                          <p className="text-sm text-gray-400 mt-1">{vuln.url}</p>
                        </div>
                      </div>
                      <p className="mt-2 text-sm">{vuln.description}</p>
                      <div className="mt-2 text-xs text-gray-400">
                        Détecté le {new Date(vuln.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Shield className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p>Aucune vulnérabilité détectée</p>
                    <p className="text-sm mt-2">Lancez un scan pour détecter les vulnérabilités de la plateforme</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Attacks Tab */}
        <TabsContent value="attacks" className="flex-1">
          <Card className="bg-gray-900 border-gray-800 h-full">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Attaques Bloquées
              </CardTitle>
            </CardHeader>
            <CardContent className="h-[calc(100%-60px)] overflow-auto">
              <div className="space-y-4">
                {robotState.attacks.length > 0 ? (
                  robotState.attacks.map((attack, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border ${
                        attack.severity === "critical"
                          ? "bg-red-900/20 border-red-800"
                          : attack.severity === "high"
                            ? "bg-orange-900/20 border-orange-800"
                            : "bg-yellow-900/20 border-yellow-800"
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="flex items-center gap-2">
                            <Badge
                              variant={
                                attack.severity === "critical" || attack.severity === "high" ? "destructive" : "default"
                              }
                            >
                              {attack.severity.toUpperCase()}
                            </Badge>
                            <h3 className="font-medium">{attack.type}</h3>
                            <Badge variant="outline" className="bg-green-900/20 text-green-400 border-green-800">
                              BLOQUÉE
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-400 mt-1">Source: {attack.source}</p>
                        </div>
                      </div>
                      <p className="mt-2 text-sm">{attack.description}</p>
                      <div className="mt-2 text-xs text-gray-400">
                        Détecté le {new Date(attack.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Shield className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p>Aucune attaque détectée</p>
                    <p className="text-sm mt-2">Le Robot Guardian protège activement votre plateforme</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
