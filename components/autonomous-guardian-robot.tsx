"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Shield, AlertTriangle, Activity, Globe, Zap, Power, AlertCircle, Play, FileCode, Layers } from "lucide-react"

interface ScanProgress {
  currentUrl: string
  progress: number
  status: string
  pagesScanned: number
  vulnerabilitiesFound: number
  currentAction: string
}

interface RobotState {
  position: { x: number; y: number }
  isWalking: boolean
  isScanning: boolean
  eyeColor: string
  mood: "happy" | "scanning" | "alert" | "sleeping" | "defending"
  currentTarget: string
  currentPage: string
}

interface Vulnerability {
  id: string
  type: string
  severity: "low" | "medium" | "high" | "critical"
  url: string
  description: string
  timestamp: string
  fixed: boolean
  attackVector: string
  payload?: string
  recommendation: string
}

interface Attack {
  id: string
  timestamp: string
  type: string
  severity: "low" | "medium" | "high" | "critical"
  source: string
  status: "blocked" | "detected" | "investigating"
  details: string
}

interface WebsitePage {
  url: string
  title: string
  status: "safe" | "vulnerable" | "unknown"
  lastScanned: string
}

export function AutonomousGuardianRobot() {
  const [robotState, setRobotState] = useState<RobotState>({
    position: { x: 50, y: 50 },
    isWalking: false,
    isScanning: false,
    eyeColor: "#00FFFF",
    mood: "happy",
    currentTarget: "",
    currentPage: "",
  })

  const [scanProgress, setScanProgress] = useState<ScanProgress>({
    currentUrl: "",
    progress: 0,
    status: "idle",
    pagesScanned: 0,
    vulnerabilitiesFound: 0,
    currentAction: "En attente...",
  })

  const [mainWebsite, setMainWebsite] = useState("https://monsite.com")
  const [isActive, setIsActive] = useState(false)
  const [scanResults, setScanResults] = useState<any[]>([])
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([])
  const [activeTab, setActiveTab] = useState("dashboard")
  const [siteStatus, setSiteStatus] = useState<"online" | "offline" | "protected">("online")
  const [activeDefense, setActiveDefense] = useState(true)
  const [attacks, setAttacks] = useState<Attack[]>([])
  const [alertVisible, setAlertVisible] = useState(false)
  const [alertMessage, setAlertMessage] = useState("")
  const [alertSeverity, setAlertSeverity] = useState<"low" | "medium" | "high" | "critical">("medium")
  const [scanMode, setScanMode] = useState<"passive" | "active">("passive")
  const [websitePages, setWebsitePages] = useState<WebsitePage[]>([])
  const [siteMap, setSiteMap] = useState<{ nodes: any[]; links: any[] }>({ nodes: [], links: [] })

  const robotRef = useRef<HTMLDivElement>(null)
  const siteMapRef = useRef<HTMLDivElement>(null)

  // Initialisation des pages du site
  useEffect(() => {
    if (mainWebsite) {
      const pages: WebsitePage[] = [
        {
          url: `${mainWebsite}`,
          title: "Accueil",
          status: "unknown",
          lastScanned: "",
        },
        {
          url: `${mainWebsite}/about`,
          title: "À propos",
          status: "unknown",
          lastScanned: "",
        },
        {
          url: `${mainWebsite}/contact`,
          title: "Contact",
          status: "unknown",
          lastScanned: "",
        },
        {
          url: `${mainWebsite}/login`,
          title: "Connexion",
          status: "unknown",
          lastScanned: "",
        },
        {
          url: `${mainWebsite}/admin`,
          title: "Administration",
          status: "unknown",
          lastScanned: "",
        },
        {
          url: `${mainWebsite}/api/users`,
          title: "API Utilisateurs",
          status: "unknown",
          lastScanned: "",
        },
        {
          url: `${mainWebsite}/products`,
          title: "Produits",
          status: "unknown",
          lastScanned: "",
        },
      ]
      setWebsitePages(pages)

      // Créer la carte du site
      const nodes = pages.map((page, index) => ({
        id: index,
        url: page.url,
        title: page.title,
      }))

      const links = [
        { source: 0, target: 1 },
        { source: 0, target: 2 },
        { source: 0, target: 3 },
        { source: 3, target: 4 },
        { source: 0, target: 6 },
        { source: 4, target: 5 },
      ]

      setSiteMap({ nodes, links })
    }
  }, [mainWebsite])

  // Animation du robot qui marche
  useEffect(() => {
    if (!robotState.isWalking || !isActive) return

    const walkAnimation = setInterval(() => {
      // Trouver une page aléatoire à visiter
      const randomPageIndex = Math.floor(Math.random() * websitePages.length)
      const randomPage = websitePages[randomPageIndex]

      setRobotState((prev) => ({
        ...prev,
        position: {
          x: Math.random() * 80 + 10,
          y: Math.random() * 60 + 20,
        },
        currentPage: randomPage.url,
      }))
    }, 3000)

    return () => clearInterval(walkAnimation)
  }, [robotState.isWalking, isActive, websitePages.length])

  // Simulation du scan
  useEffect(() => {
    if (!isActive) return

    const scanCycle = async () => {
      // Démarrer le scan du site principal
      setRobotState((prev) => ({
        ...prev,
        isWalking: true,
        mood: "scanning",
        eyeColor: "#FFD700",
        currentTarget: mainWebsite,
      }))

      setScanProgress({
        currentUrl: mainWebsite,
        progress: 0,
        status: "walking",
        pagesScanned: 0,
        vulnerabilitiesFound: 0,
        currentAction: `🚶 Exploration du site ${mainWebsite}...`,
      })

      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Scanner chaque page
      for (let i = 0; i < websitePages.length; i++) {
        const page = websitePages[i]

        // Robot se déplace vers la page
        setRobotState((prev) => ({
          ...prev,
          isWalking: true,
          mood: "scanning",
          eyeColor: "#FFD700",
          currentTarget: page.url,
          currentPage: page.url,
        }))

        setScanProgress({
          currentUrl: page.url,
          progress: (i / websitePages.length) * 100,
          status: "scanning",
          pagesScanned: i,
          vulnerabilitiesFound: vulnerabilities.length,
          currentAction: `🔍 Scan de ${page.title}...`,
        })

        await new Promise((resolve) => setTimeout(resolve, 2000))

        // Robot commence le scan approfondi
        setRobotState((prev) => ({
          ...prev,
          isWalking: false,
          isScanning: true,
          eyeColor: scanMode === "active" ? "#FF4500" : "#00FFFF",
        }))

        // Mise à jour du statut de la page
        setWebsitePages((prev) =>
          prev.map((p) =>
            p.url === page.url
              ? {
                  ...p,
                  status: Math.random() > 0.8 ? "vulnerable" : "safe",
                  lastScanned: new Date().toISOString(),
                }
              : p,
          ),
        )

        // Si en mode actif, tester les vulnérabilités
        if (scanMode === "active" && Math.random() > 0.7) {
          // Simuler la découverte d'une vulnérabilité
          const vulnTypes = [
            {
              type: "SQL Injection",
              description: "Possibilité d'injection SQL dans le paramètre id",
              attackVector: "Paramètre GET",
              payload: "id=1' OR '1'='1",
              recommendation: "Utiliser des requêtes préparées et valider les entrées",
            },
            {
              type: "XSS",
              description: "Vulnérabilité Cross-Site Scripting dans le formulaire de commentaire",
              attackVector: "Champ de commentaire",
              payload: "<script>alert('XSS')</script>",
              recommendation: "Échapper les sorties HTML et utiliser Content-Security-Policy",
            },
            {
              type: "CSRF",
              description: "Absence de protection CSRF sur le formulaire de modification",
              attackVector: "Formulaire POST",
              recommendation: "Implémenter des tokens CSRF et vérifier l'origine",
            },
            {
              type: "Insecure Direct Object Reference",
              description: "Accès possible aux données d'autres utilisateurs en modifiant l'ID",
              attackVector: "Paramètre d'URL",
              payload: "user_id=2",
              recommendation: "Vérifier les autorisations pour chaque accès aux ressources",
            },
          ]

          const randomVuln = vulnTypes[Math.floor(Math.random() * vulnTypes.length)]
          const severity = ["low", "medium", "high", "critical"][Math.floor(Math.random() * 4)] as any

          const newVulnerability: Vulnerability = {
            id: `vuln-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
            type: randomVuln.type,
            severity,
            url: page.url,
            description: randomVuln.description,
            timestamp: new Date().toISOString(),
            fixed: false,
            attackVector: randomVuln.attackVector,
            payload: randomVuln.payload,
            recommendation: randomVuln.recommendation,
          }

          setVulnerabilities((prev) => [...prev, newVulnerability])

          // Changer l'état du robot selon la sévérité
          if (severity === "critical" || severity === "high") {
            setRobotState((prev) => ({
              ...prev,
              eyeColor: "#FF0000",
              mood: "alert",
            }))

            // Afficher une alerte
            setAlertMessage(
              `⚠️ Vulnérabilité ${severity === "critical" ? "CRITIQUE" : "IMPORTANTE"} détectée sur ${page.title}!`,
            )
            setAlertSeverity(severity)
            setAlertVisible(true)

            // Masquer l'alerte après 5 secondes
            setTimeout(() => setAlertVisible(false), 5000)
          }
        }

        await new Promise((resolve) => setTimeout(resolve, 1500))
      }

      // Scan terminé
      setScanProgress({
        currentUrl: mainWebsite,
        progress: 100,
        status: "completed",
        pagesScanned: websitePages.length,
        vulnerabilitiesFound: vulnerabilities.length,
        currentAction: "✅ Scan terminé",
      })

      // Sauvegarder les résultats
      const result = {
        website: mainWebsite,
        timestamp: new Date().toISOString(),
        vulnerabilities: vulnerabilities.length,
        pagesScanned: websitePages.length,
        status: vulnerabilities.length > 3 ? "high_risk" : vulnerabilities.length > 0 ? "medium_risk" : "safe",
      }

      setScanResults((prev) => [result, ...prev.slice(0, 9)]) // Garder 10 derniers

      // Robot retourne en mode veille/patrouille
      setRobotState((prev) => ({
        ...prev,
        isScanning: false,
        isWalking: true,
        eyeColor: "#00FFFF",
        mood: "happy",
      }))

      // Simuler des attaques aléatoires
      const attackSimulation = setInterval(() => {
        if (Math.random() > 0.7 && isActive) {
          simulateAttack()
        }
      }, 15000)

      return () => clearInterval(attackSimulation)
    }

    scanCycle()

    // Démarrer la patrouille continue
    const patrolInterval = setInterval(() => {
      if (isActive && !robotState.isScanning) {
        setRobotState((prev) => ({
          ...prev,
          isWalking: true,
        }))
      }
    }, 5000)

    return () => clearInterval(patrolInterval)
  }, [isActive, mainWebsite, scanMode, websitePages.length])

  const simulateAttack = () => {
    const attackTypes = [
      {
        type: "Brute Force",
        details: "Tentative de connexion répétée sur /login",
        severity: "medium",
      },
      {
        type: "SQL Injection",
        details: "Tentative d'injection SQL sur /api/users",
        severity: "critical",
      },
      {
        type: "DDoS",
        details: "Augmentation anormale du trafic",
        severity: "high",
      },
      {
        type: "XSS",
        details: "Tentative d'injection de script sur /contact",
        severity: "high",
      },
      {
        type: "Path Traversal",
        details: "Tentative d'accès à ../../../etc/passwd",
        severity: "critical",
      },
    ]

    const randomAttack = attackTypes[Math.floor(Math.random() * attackTypes.length)]
    const attackSeverity = randomAttack.severity as "low" | "medium" | "high" | "critical"
    const attackStatus = activeDefense ? "blocked" : Math.random() > 0.5 ? "detected" : "investigating"

    const newAttack: Attack = {
      id: `attack-${Date.now()}`,
      timestamp: new Date().toISOString(),
      type: randomAttack.type,
      severity: attackSeverity,
      source: `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(
        Math.random() * 255,
      )}.${Math.floor(Math.random() * 255)}`,
      status: attackStatus,
      details: randomAttack.details,
    }

    setAttacks((prev) => [newAttack, ...prev.slice(0, 19)])

    // Réaction du robot
    setRobotState((prev) => ({
      ...prev,
      mood: "defending",
      eyeColor: "#FF0000",
      isScanning: false,
      isWalking: false,
    }))

    // Afficher une alerte
    setAlertMessage(`🚨 ATTAQUE DÉTECTÉE: ${randomAttack.type}`)
    setAlertSeverity(attackSeverity)
    setAlertVisible(true)

    // Si défense active et attaque critique, mettre le site en mode protégé
    if (activeDefense && (attackSeverity === "critical" || attackSeverity === "high")) {
      setSiteStatus("protected")
      setTimeout(() => {
        setSiteStatus("online")
        setRobotState((prev) => ({
          ...prev,
          mood: "happy",
          eyeColor: "#00FFFF",
          isWalking: true,
        }))
      }, 5000)
    }

    // Masquer l'alerte après 5 secondes
    setTimeout(() => {
      setAlertVisible(false)
      setRobotState((prev) => ({
        ...prev,
        mood: "scanning",
        eyeColor: "#00FFFF",
        isWalking: true,
      }))
    }, 5000)
  }

  const toggleRobot = () => {
    setIsActive(!isActive)
    if (!isActive) {
      setRobotState((prev) => ({
        ...prev,
        mood: "happy",
        eyeColor: "#00FFFF",
        isWalking: true,
      }))
    } else {
      setRobotState((prev) => ({
        ...prev,
        mood: "sleeping",
        eyeColor: "#666666",
        isWalking: false,
        isScanning: false,
      }))
    }
  }

  const toggleSiteStatus = () => {
    setSiteStatus(siteStatus === "online" ? "offline" : "online")
  }

  const markAsFixed = (id: string) => {
    setVulnerabilities((prev) => prev.map((v) => (v.id === id ? { ...v, fixed: true } : v)))
  }

  const toggleScanMode = () => {
    setScanMode(scanMode === "passive" ? "active" : "passive")
  }

  const getRobotEyes = () => {
    const { mood, eyeColor } = robotState

    switch (mood) {
      case "scanning":
        return (
          <div className="flex gap-2">
            <div className={`w-3 h-3 rounded-full animate-pulse`} style={{ backgroundColor: eyeColor }} />
            <div className={`w-3 h-3 rounded-full animate-pulse`} style={{ backgroundColor: eyeColor }} />
          </div>
        )
      case "alert":
        return (
          <div className="flex gap-2">
            <div className={`w-3 h-3 rounded-full animate-bounce`} style={{ backgroundColor: "#FF0000" }} />
            <div className={`w-3 h-3 rounded-full animate-bounce`} style={{ backgroundColor: "#FF0000" }} />
          </div>
        )
      case "defending":
        return (
          <div className="flex gap-2">
            <div className={`w-3 h-3 rounded-full animate-ping`} style={{ backgroundColor: "#FF0000" }} />
            <div className={`w-3 h-3 rounded-full animate-ping`} style={{ backgroundColor: "#FF0000" }} />
          </div>
        )
      case "sleeping":
        return (
          <div className="flex gap-2">
            <div className="w-4 h-1 bg-gray-500 rounded-full" />
            <div className="w-4 h-1 bg-gray-500 rounded-full" />
          </div>
        )
      default:
        return (
          <div className="flex gap-2">
            <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: eyeColor }} />
            <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: eyeColor }} />
          </div>
        )
    }
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
            <p className="text-gray-400">Surveillance autonome et défense active de votre site web</p>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center mr-4">
              <div
                className={`w-3 h-3 rounded-full mr-2 ${
                  siteStatus === "online"
                    ? "bg-green-500"
                    : siteStatus === "offline"
                      ? "bg-red-500"
                      : "bg-yellow-500 animate-pulse"
                }`}
              />
              <span className="text-sm">
                Site {siteStatus === "online" ? "En ligne" : siteStatus === "offline" ? "Hors ligne" : "Mode protégé"}
              </span>
            </div>

            <Button
              onClick={toggleRobot}
              className={`${isActive ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"}`}
            >
              {isActive ? (
                <>
                  <Shield className="w-4 h-4 mr-2" />
                  Arrêter Guardian
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Activer Guardian
                </>
              )}
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

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="grid grid-cols-4 mb-4">
          <TabsTrigger value="dashboard" className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="sitemap" className="flex items-center gap-2">
            <Layers className="w-4 h-4" />
            Carte du Site
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
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Zone du robot animé */}
            <div className="lg:col-span-2">
              <Card className="bg-gray-900 border-gray-800 h-80 relative overflow-hidden">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Activity className="w-4 h-4" />
                    Robot Guardian en Patrouille
                  </CardTitle>
                </CardHeader>
                <CardContent className="relative h-full">
                  {/* Grille de fond */}
                  <div className="absolute inset-0 opacity-20">
                    <div className="grid grid-cols-8 grid-rows-6 h-full w-full">
                      {Array.from({ length: 48 }).map((_, i) => (
                        <div key={i} className="border border-gray-700" />
                      ))}
                    </div>
                  </div>

                  {/* Pages du site représentées */}
                  {websitePages.map((page, index) => (
                    <div
                      key={page.url}
                      className={`absolute w-10 h-10 rounded-lg flex items-center justify-center text-xs ${
                        robotState.currentPage === page.url
                          ? "bg-yellow-500 animate-pulse"
                          : page.status === "vulnerable"
                            ? "bg-red-500"
                            : page.status === "safe"
                              ? "bg-green-500"
                              : "bg-blue-500"
                      }`}
                      style={{
                        left: `${15 + (index % 4) * 23}%`,
                        top: `${20 + Math.floor(index / 4) * 30}%`,
                      }}
                    >
                      <FileCode className="w-5 h-5" />
                      <div className="absolute -bottom-6 text-xs whitespace-nowrap">{page.title.substring(0, 10)}</div>
                    </div>
                  ))}

                  {/* Robot animé */}
                  <div
                    ref={robotRef}
                    className={`absolute transition-all duration-2000 ease-in-out ${
                      robotState.isWalking ? "animate-bounce" : ""
                    }`}
                    style={{
                      left: `${robotState.position.x}%`,
                      top: `${robotState.position.y}%`,
                      transform: "translate(-50%, -50%)",
                      zIndex: 10,
                    }}
                  >
                    <div className="relative">
                      {/* Corps du robot */}
                      <div className="w-16 h-20 bg-gradient-to-b from-gray-300 to-gray-400 rounded-2xl shadow-lg">
                        {/* Tête */}
                        <div className="w-12 h-12 bg-gradient-to-b from-gray-200 to-gray-300 rounded-xl mx-auto -mt-2 relative">
                          {/* Écran/Visage */}
                          <div className="w-10 h-8 bg-gray-900 rounded-lg mx-auto mt-2 flex items-center justify-center">
                            {getRobotEyes()}
                          </div>

                          {/* Bouche */}
                          <div
                            className={`w-4 h-1 rounded-full mx-auto mt-1 ${
                              robotState.mood === "alert" || robotState.mood === "defending"
                                ? "bg-red-400"
                                : "bg-cyan-400"
                            }`}
                          />
                        </div>

                        {/* Bras */}
                        <div className="absolute -left-2 top-4 w-3 h-8 bg-gray-300 rounded-full" />
                        <div className="absolute -right-2 top-4 w-3 h-8 bg-gray-300 rounded-full" />
                      </div>

                      {/* Effets de scan */}
                      {robotState.isScanning && (
                        <div className="absolute -inset-4">
                          <div
                            className="w-full h-full border-2 rounded-full animate-ping"
                            style={{ borderColor: robotState.eyeColor }}
                          />
                          <div
                            className="absolute inset-2 border rounded-full animate-pulse"
                            style={{ borderColor: robotState.eyeColor }}
                          />
                        </div>
                      )}

                      {/* Effets de défense */}
                      {robotState.mood === "defending" && (
                        <div className="absolute -inset-8">
                          <div className="w-full h-full border-2 border-red-500 rounded-full animate-ping" />
                          <div className="absolute inset-4 border border-red-400 rounded-full animate-pulse" />
                          <div className="absolute inset-6 border-2 border-red-600 rounded-full animate-ping" />
                        </div>
                      )}

                      {/* Indicateur de page */}
                      {robotState.currentPage && (
                        <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 px-2 py-1 rounded text-xs whitespace-nowrap">
                          🔍 {robotState.currentPage.split("/").pop() || "Accueil"}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Barre de progression du scan */}
              {scanProgress.status !== "idle" && (
                <Card className="bg-gray-900 border-gray-800 mt-4">
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{scanProgress.currentAction}</span>
                        <Badge variant="outline">{scanProgress.pagesScanned} pages scannées</Badge>
                      </div>

                      <Progress value={scanProgress.progress} className="h-2" />

                      <div className="flex justify-between text-xs text-gray-400">
                        <span>
                          Mode: {scanMode === "passive" ? "Passif (observation)" : "Actif (tests d'intrusion)"}
                        </span>
                        <span>{scanProgress.vulnerabilitiesFound} vulnérabilités trouvées</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Panneau de contrôle */}
            <div className="space-y-4">
              {/* Configuration du site */}
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Globe className="w-4 h-4" />
                    Site à Protéger
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      value={mainWebsite}
                      onChange={(e) => setMainWebsite(e.target.value)}
                      placeholder="https://monsite.com"
                      className="bg-gray-800 border-gray-700 text-white"
                    />
                    <Button onClick={toggleSiteStatus} size="sm" variant="outline">
                      {siteStatus === "online" ? <Power className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </Button>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Switch id="defense-mode" checked={activeDefense} onCheckedChange={setActiveDefense} />
                        <Label htmlFor="defense-mode">Défense active</Label>
                      </div>
                      <Badge variant={activeDefense ? "default" : "outline"}>
                        {activeDefense ? "Activée" : "Désactivée"}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Switch id="scan-mode" checked={scanMode === "active"} onCheckedChange={toggleScanMode} />
                        <Label htmlFor="scan-mode">Mode scan actif</Label>
                      </div>
                      <Badge variant={scanMode === "active" ? "destructive" : "outline"}>
                        {scanMode === "active" ? "Actif" : "Passif"}
                      </Badge>
                    </div>

                    <div className="text-xs text-gray-400 mt-2">
                      {scanMode === "active"
                        ? "⚠️ Le mode actif teste réellement les vulnérabilités"
                        : "ℹ️ Le mode passif observe sans tester d'exploits"}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Statistiques */}
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Activity className="w-4 h-4" />
                    Statistiques
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-gray-800 p-3 rounded">
                      <div className="text-xs text-gray-400">Pages surveillées</div>
                      <div className="text-xl font-bold">{websitePages.length}</div>
                    </div>
                    <div className="bg-gray-800 p-3 rounded">
                      <div className="text-xs text-gray-400">Vulnérabilités</div>
                      <div className="text-xl font-bold">{vulnerabilities.length}</div>
                    </div>
                    <div className="bg-gray-800 p-3 rounded">
                      <div className="text-xs text-gray-400">Attaques bloquées</div>
                      <div className="text-xl font-bold">{attacks.filter((a) => a.status === "blocked").length}</div>
                    </div>
                    <div className="bg-gray-800 p-3 rounded">
                      <div className="text-xs text-gray-400">Risque global</div>
                      <div
                        className={`text-xl font-bold ${
                          vulnerabilities.length > 5
                            ? "text-red-500"
                            : vulnerabilities.length > 2
                              ? "text-yellow-500"
                              : "text-green-500"
                        }`}
                      >
                        {vulnerabilities.length > 5 ? "Élevé" : vulnerabilities.length > 2 ? "Moyen" : "Faible"}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Dernières activités */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm">
                <Activity className="w-4 h-4" />
                Dernières Activités
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {[...attacks.slice(0, 3), ...vulnerabilities.slice(0, 2)]
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
                          {isAttack
                            ? (item as Attack).status === "blocked"
                              ? "Bloquée"
                              : "Détectée"
                            : (item as Vulnerability).fixed
                              ? "Corrigée"
                              : "Active"}
                        </Badge>
                      </div>
                    )
                  })}

                {attacks.length === 0 && vulnerabilities.length === 0 && (
                  <div className="text-center py-4 text-gray-400">
                    <Shield className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Aucune activité récente</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Site Map Tab */}
        <TabsContent value="sitemap" className="flex-1">
          <Card className="bg-gray-900 border-gray-800 h-full">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2">
                <Layers className="w-4 h-4" />
                Carte du Site et Pages Surveillées
              </CardTitle>
            </CardHeader>
            <CardContent className="h-[calc(100%-60px)] overflow-auto">
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Visualisation de la carte */}
                  <div className="bg-gray-800 rounded-lg p-4 h-80 relative" ref={siteMapRef}>
                    {/* Représentation simplifiée de la carte du site */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="relative w-full h-full">
                        {/* Liens entre les pages */}
                        {siteMap.links.map((link, index) => {
                          const source = siteMap.nodes[link.source]
                          const target = siteMap.nodes[link.target]
                          // Positions simplifiées
                          const sourceX = 50 + (source.id % 3) * 80 - 120
                          const sourceY = 50 + Math.floor(source.id / 3) * 70 - 70
                          const targetX = 50 + (target.id % 3) * 80 - 120
                          const targetY = 50 + Math.floor(target.id / 3) * 70 - 70

                          return (
                            <svg key={index} className="absolute inset-0 w-full h-full" style={{ zIndex: 1 }}>
                              <line
                                x1={`${sourceX + 25}%`}
                                y1={`${sourceY + 25}%`}
                                x2={`${targetX + 25}%`}
                                y2={`${targetY + 25}%`}
                                stroke="#4B5563"
                                strokeWidth="2"
                              />
                            </svg>
                          )
                        })}

                        {/* Nœuds des pages */}
                        {siteMap.nodes.map((node) => {
                          const page = websitePages.find((p) => p.url === node.url)
                          const x = 50 + (node.id % 3) * 80 - 120
                          const y = 50 + Math.floor(node.id / 3) * 70 - 70

                          return (
                            <div
                              key={node.id}
                              className={`absolute w-12 h-12 rounded-lg flex items-center justify-center ${
                                page?.status === "vulnerable"
                                  ? "bg-red-500"
                                  : page?.status === "safe"
                                    ? "bg-green-500"
                                    : "bg-blue-500"
                              }`}
                              style={{
                                left: `${x}%`,
                                top: `${y}%`,
                                zIndex: 2,
                              }}
                            >
                              <div className="text-xs text-center">
                                <FileCode className="w-6 h-6 mx-auto" />
                                <div className="mt-1 text-[10px] whitespace-nowrap">{node.title.substring(0, 8)}</div>
                              </div>
                            </div>
                          )
                        })}

                        {/* Robot sur la carte */}
                        {robotState.currentPage && (
                          <div
                            className="absolute w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center animate-pulse"
                            style={{
                              left: `${
                                50 +
                                (siteMap.nodes.findIndex((n) => n.url === robotState.currentPage) % 3) * 80 -
                                120 +
                                15
                              }%`,
                              top: `${
                                50 +
                                Math.floor(siteMap.nodes.findIndex((n) => n.url === robotState.currentPage) / 3) * 70 -
                                70 +
                                15
                              }%`,
                              zIndex: 3,
                            }}
                          >
                            <div className="w-6 h-6 rounded-full" style={{ backgroundColor: robotState.eyeColor }} />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Légende et statistiques */}
                  <div className="space-y-4">
                    <div className="bg-gray-800 rounded-lg p-4">
                      <h3 className="text-sm font-medium mb-2">Légende</h3>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded-full bg-green-500" />
                          <span className="text-sm">Page sécurisée</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded-full bg-red-500" />
                          <span className="text-sm">Page vulnérable</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded-full bg-blue-500" />
                          <span className="text-sm">Page non scannée</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded-full bg-gray-300" />
                          <span className="text-sm">Robot Guardian</span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-800 rounded-lg p-4">
                      <h3 className="text-sm font-medium mb-2">Statistiques des Pages</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Total des pages</span>
                          <span className="text-sm font-medium">{websitePages.length}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Pages sécurisées</span>
                          <span className="text-sm font-medium">
                            {websitePages.filter((p) => p.status === "safe").length}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Pages vulnérables</span>
                          <span className="text-sm font-medium text-red-400">
                            {websitePages.filter((p) => p.status === "vulnerable").length}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Pages non scannées</span>
                          <span className="text-sm font-medium">
                            {websitePages.filter((p) => p.status === "unknown").length}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Liste des pages */}
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-sm font-medium mb-2">Pages du Site</h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {websitePages.map((page) => (
                      <div key={page.url} className="flex items-center justify-between bg-gray-700 p-2 rounded">
                        <div className="flex items-center gap-2">
                          <div
                            className={`w-3 h-3 rounded-full ${
                              page.status === "vulnerable"
                                ? "bg-red-500"
                                : page.status === "safe"
                                  ? "bg-green-500"
                                  : "bg-blue-500"
                            }`}
                          />
                          <div>
                            <p className="text-sm font-medium">{page.title}</p>
                            <p className="text-xs text-gray-400">{page.url}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">
                            {page.status === "vulnerable"
                              ? "Vulnérable"
                              : page.status === "safe"
                                ? "Sécurisée"
                                : "Non scannée"}
                          </Badge>
                          {page.lastScanned && (
                            <span className="text-xs text-gray-400">
                              {new Date(page.lastScanned).toLocaleTimeString()}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
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
                {vulnerabilities.length > 0 ? (
                  vulnerabilities.map((vuln) => (
                    <div
                      key={vuln.id}
                      className={`p-4 rounded-lg border ${
                        vuln.fixed
                          ? "bg-gray-800 border-gray-700"
                          : vuln.severity === "critical"
                            ? "bg-red-900/20 border-red-800"
                            : vuln.severity === "high"
                              ? "bg-orange-900/20 border-orange-800"
                              : vuln.severity === "medium"
                                ? "bg-yellow-900/20 border-yellow-800"
                                : "bg-blue-900/20 border-blue-800"
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="flex items-center gap-2">
                            <Badge
                              variant={
                                vuln.severity === "critical"
                                  ? "destructive"
                                  : vuln.severity === "high"
                                    ? "destructive"
                                    : vuln.severity === "medium"
                                      ? "default"
                                      : "outline"
                              }
                            >
                              {vuln.severity.toUpperCase()}
                            </Badge>
                            <h3 className="font-medium">{vuln.type}</h3>
                            {vuln.fixed && (
                              <Badge variant="outline" className="bg-green-900/20 text-green-400 border-green-800">
                                CORRIGÉ
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-400 mt-1">{vuln.url}</p>
                        </div>
                        {!vuln.fixed && (
                          <Button size="sm" variant="outline" onClick={() => markAsFixed(vuln.id)}>
                            Marquer comme corrigé
                          </Button>
                        )}
                      </div>
                      <p className="mt-2 text-sm">{vuln.description}</p>
                      <div className="mt-2 space-y-2">
                        <div className="flex items-center gap-2 text-xs">
                          <span className="font-medium">Vecteur d'attaque:</span>
                          <span className="text-gray-400">{vuln.attackVector}</span>
                        </div>
                        {vuln.payload && (
                          <div className="flex items-center gap-2 text-xs">
                            <span className="font-medium">Payload:</span>
                            <code className="bg-gray-800 px-2 py-1 rounded text-red-400">{vuln.payload}</code>
                          </div>
                        )}
                        <div className="flex items-center gap-2 text-xs">
                          <span className="font-medium">Recommandation:</span>
                          <span className="text-green-400">{vuln.recommendation}</span>
                        </div>
                      </div>
                      <div className="mt-2 text-xs text-gray-400">
                        Détecté le {new Date(vuln.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Shield className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p>Aucune vulnérabilité détectée</p>
                    <p className="text-sm mt-2">
                      Activez le Robot Guardian et passez en mode scan actif pour détecter les vulnérabilités
                    </p>
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
                Attaques Détectées
              </CardTitle>
            </CardHeader>
            <CardContent className="h-[calc(100%-60px)] overflow-auto">
              <div className="space-y-4">
                {attacks.length > 0 ? (
                  attacks.map((attack) => (
                    <div
                      key={attack.id}
                      className={`p-4 rounded-lg border ${
                        attack.status === "blocked"
                          ? "bg-gray-800 border-gray-700"
                          : attack.severity === "critical"
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
                            <Badge
                              variant={
                                attack.status === "blocked"
                                  ? "outline"
                                  : attack.status === "investigating"
                                    ? "default"
                                    : "destructive"
                              }
                              className={
                                attack.status === "blocked" ? "bg-green-900/20 text-green-400 border-green-800" : ""
                              }
                            >
                              {attack.status === "blocked"
                                ? "BLOQUÉE"
                                : attack.status === "investigating"
                                  ? "EN ANALYSE"
                                  : "DÉTECTÉE"}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-400 mt-1">Source: {attack.source}</p>
                        </div>
                      </div>
                      <p className="mt-2 text-sm">{attack.details}</p>
                      <div className="mt-2 text-xs text-gray-400">
                        Détecté le {new Date(attack.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Shield className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p>Aucune attaque détectée</p>
                    <p className="text-sm mt-2">
                      Le Robot Guardian surveille activement votre site contre les attaques
                    </p>
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
