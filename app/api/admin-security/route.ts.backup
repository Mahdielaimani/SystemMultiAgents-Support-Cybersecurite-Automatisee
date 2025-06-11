// app/api/admin-security/route.ts
import { NextRequest, NextResponse } from "next/server"

// Interface pour les requêtes admin
interface AdminLoginRequest {
  username: string
  password: string
}

interface AdminActionRequest {
  action: "block_system" | "unblock_system" | "generate_report" | "get_status"
  reason?: string
  severity?: string
}

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

interface UserActivity {
  session_id: string
  messages_count: number
  last_activity: string
  threat_score: number
  blocked: boolean
  location?: string
}

// Configuration sécurisée
const ADMIN_CREDENTIALS = {
  username: process.env.ADMIN_USERNAME || "admin",
  password: process.env.ADMIN_PASSWORD || "security123"
}

const API_BASE_URL = process.env.BACKEND_URL || "http://localhost:8000"

// État système global
let systemState = {
  blocked: false,
  threat_level: "safe" as "safe" | "warning" | "danger",
  active_threats: [] as any[],
  last_scan: new Date().toISOString(),
  models_status: {
    vulnerability_classifier: "active" as "active" | "inactive" | "error",
    network_analyzer: "active" as "active" | "inactive" | "error", 
    intent_classifier: "active" as "active" | "inactive" | "error"
  }
}

// Simulation de base de données temporaire pour les alertes
let mockAlerts: SecurityAlert[] = [
  {
    id: "alert_001",
    type: "vulnerability",
    severity: "critical", 
    message: "Tentative d'injection SQL détectée",
    timestamp: new Date(Date.now() - 300000).toISOString(),
    action_taken: "Requête bloquée automatiquement",
    details: { vulnerability_type: "SQL_INJECTION", confidence: 0.92 },
    user_session: "user_123"
  },
  {
    id: "alert_002",
    type: "intent",
    severity: "high",
    message: "Intention malveillante détectée",
    timestamp: new Date(Date.now() - 600000).toISOString(),
    action_taken: "Session utilisateur surveillée",
    details: { intent: "Malicious", confidence: 0.87 },
    user_session: "user_456"
  },
  {
    id: "alert_003",
    type: "network", 
    severity: "medium",
    message: "Trafic réseau suspect détecté",
    timestamp: new Date(Date.now() - 900000).toISOString(),
    action_taken: "Surveillance renforcée activée",
    details: { traffic_type: "SUSPICIOUS", confidence: 0.75 }
  }
]

let userActivities: UserActivity[] = [
  {
    session_id: "user_123",
    messages_count: 15,
    last_activity: new Date(Date.now() - 120000).toISOString(),
    threat_score: 0.8,
    blocked: true,
    location: "France"
  },
  {
    session_id: "user_456",
    messages_count: 8,
    last_activity: new Date(Date.now() - 300000).toISOString(), 
    threat_score: 0.9,
    blocked: true,
    location: "Unknown"
  },
  {
    session_id: "user_789",
    messages_count: 3,
    last_activity: new Date(Date.now() - 60000).toISOString(),
    threat_score: 0.1,
    blocked: false,
    location: "Maroc"
  }
]

// Fonction pour valider les credentials admin
function validateAdminCredentials(username: string, password: string): boolean {
  return username === ADMIN_CREDENTIALS.username && password === ADMIN_CREDENTIALS.password
}

// Fonction pour générer un rapport de sécurité
function generateSecurityReport() {
  const now = new Date()
  
  const report = {
    generated_at: now.toISOString(),
    generated_by: "Security Admin System",
    report_id: `SEC_RPT_${now.getTime()}`,
    
    executive_summary: {
      total_alerts: mockAlerts.length,
      critical_threats: mockAlerts.filter(a => a.severity === "critical").length,
      blocked_users: userActivities.filter(u => u.blocked).length,
      system_status: systemState.blocked ? "BLOCKED" : "OPERATIONAL",
      threat_level: systemState.threat_level.toUpperCase()
    },
    
    system_status: systemState,
    
    alerts_breakdown: {
      by_severity: {
        critical: mockAlerts.filter(a => a.severity === "critical").length,
        high: mockAlerts.filter(a => a.severity === "high").length,
        medium: mockAlerts.filter(a => a.severity === "medium").length,
        low: mockAlerts.filter(a => a.severity === "low").length
      },
      by_type: {
        vulnerability: mockAlerts.filter(a => a.type === "vulnerability").length,
        network: mockAlerts.filter(a => a.type === "network").length,
        intent: mockAlerts.filter(a => a.type === "intent").length
      }
    },
    
    user_activities: {
      total_sessions: userActivities.length,
      active_sessions: userActivities.filter(u => !u.blocked).length,
      blocked_sessions: userActivities.filter(u => u.blocked).length,
      high_risk_sessions: userActivities.filter(u => u.threat_score > 0.7).length,
      detailed_activities: userActivities
    },
    
    ai_models_performance: {
      vulnerability_classifier: {
        status: systemState.models_status.vulnerability_classifier,
        accuracy: "99.2%",
        detections: mockAlerts.filter(a => a.type === "vulnerability").length,
        last_update: systemState.last_scan
      },
      network_analyzer: {
        status: systemState.models_status.network_analyzer,
        accuracy: "97.8%",
        detections: mockAlerts.filter(a => a.type === "network").length,
        last_update: systemState.last_scan
      },
      intent_classifier: {
        status: systemState.models_status.intent_classifier,
        accuracy: "95.4%",
        detections: mockAlerts.filter(a => a.type === "intent").length,
        last_update: systemState.last_scan
      }
    },
    
    detailed_alerts: mockAlerts,
    
    security_metrics: {
      threats_blocked: mockAlerts.filter(a => a.action_taken.includes("bloqué")).length,
      false_positives: 2,
      response_time_avg: "1.2s",
      uptime: "99.98%"
    },
    
    recommendations: [
      "Maintenir la surveillance accrue des sessions à haut risque",
      "Considérer l'ajout de règles de filtrage supplémentaires pour les injections SQL",
      "Planifier une formation de sensibilisation à la sécurité pour les utilisateurs",
      "Évaluer l'efficacité des modèles IA et envisager des mises à jour",
      "Implémenter des alertes en temps réel pour les administrateurs",
      "Renforcer les politiques de mots de passe et d'authentification"
    ],
    
    next_actions: [
      "Révision des politiques de sécurité dans 30 jours",
      "Mise à jour des modèles de détection prévue",
      "Audit de sécurité complet recommandé",
      "Formation équipe sécurité planifiée"
    ]
  }
  
  return report
}

// POST - Actions d'administration
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, username, password, reason, severity } = body
    
    // Connexion admin
    if (action === "login") {
      if (!validateAdminCredentials(username, password)) {
        return NextResponse.json(
          { error: "Credentials invalides" },
          { status: 401 }
        )
      }
      
      return NextResponse.json({
        success: true,
        message: "Connexion réussie",
        admin_level: "full_access",
        session_token: `admin_${Date.now()}`
      })
    }
    
    // Actions système (nécessitent validation)
    switch (action) {
      case "block_system":
        try {
          // Appeler l'API backend si disponible
          const response = await fetch(`${API_BASE_URL}/api/cybersecurity/block`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              reason: reason || "Blocage manuel par administrateur",
              severity: severity || "critical"
            })
          })
          
          // Mettre à jour l'état local
          systemState.blocked = true
          systemState.threat_level = "danger"
          
          // Ajouter une alerte système
          const blockAlert = {
            id: `alert_${Date.now()}`,
            type: "system",
            severity: "critical",
            message: `Système bloqué: ${reason || "Blocage manuel"}`,
            timestamp: new Date().toISOString(),
            action_taken: "Système mis en mode sécurisé",
            details: { admin_action: true }
          } as const
          mockAlerts.unshift(blockAlert)
          
          return NextResponse.json({
            success: true,
            message: "Système bloqué avec succès",
            system_state: systemState
          })
        } catch (error) {
          console.error("Erreur blocage système:", error)
          return NextResponse.json(
            { error: "Erreur lors du blocage" },
            { status: 500 }
          )
        }
      
      case "unblock_system":
        try {
          // Appeler l'API backend si disponible
          await fetch(`${API_BASE_URL}/api/cybersecurity/unblock`, {
            method: "POST"
          })
          
          // Mettre à jour l'état local
          systemState.blocked = false
          systemState.threat_level = "safe"
          systemState.active_threats = []
          
          // Débloquer tous les utilisateurs
          userActivities.forEach(user => {
            if (user.blocked) {
              user.blocked = false
              user.threat_score = Math.max(0.1, user.threat_score - 0.3)
            }
          })
          
          return NextResponse.json({
            success: true,
            message: "Système débloqué avec succès",
            system_state: systemState
          })
        } catch (error) {
          console.error("Erreur déblocage système:", error)
          return NextResponse.json(
            { error: "Erreur lors du déblocage" },
            { status: 500 }
          )
        }
      
      case "generate_report":
        try {
          const report = generateSecurityReport()
          
          return NextResponse.json({
            success: true,
            report: report,
            download_ready: true
          })
        } catch (error) {
          console.error("Erreur génération rapport:", error)
          return NextResponse.json(
            { error: "Erreur lors de la génération du rapport" },
            { status: 500 }
          )
        }
      
      case "add_alert":
        // Ajouter une nouvelle alerte (pour simulation)
        const newAlert: SecurityAlert = {
          id: `alert_${Date.now()}`,
          type: (body.type as SecurityAlert["type"]) || "vulnerability",
          severity: (body.severity as SecurityAlert["severity"]) || "medium",
          message: body.message || "Nouvelle menace détectée",
          timestamp: new Date().toISOString(),
          action_taken: body.action_taken || "Alerte créée",
          details: body.details || {},
          user_session: body.user_session
        }
        mockAlerts.unshift(newAlert)
        
        return NextResponse.json({
          success: true,
          alert: newAlert,
          total_alerts: mockAlerts.length
        })
      
      default:
        return NextResponse.json(
          { error: "Action non reconnue" },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error("Erreur API admin:", error)
    return NextResponse.json(
      { error: "Erreur interne du serveur" },
      { status: 500 }
    )
  }
}

// GET - Récupérer le statut et les données
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const dataType = searchParams.get("type") || "all"
    
    const responseData: any = {
      timestamp: new Date().toISOString(),
      system_state: systemState
    }
    
    switch (dataType) {
      case "alerts":
        responseData.alerts = mockAlerts
        responseData.alerts_count = mockAlerts.length
        break
        
      case "users":
        responseData.user_activities = userActivities
        responseData.active_users = userActivities.filter(u => !u.blocked).length
        responseData.blocked_users = userActivities.filter(u => u.blocked).length
        break
        
      case "models":
        responseData.models_status = systemState.models_status
        responseData.models_performance = {
          vulnerability_classifier: {
            accuracy: "99.2%",
            detections: mockAlerts.filter(a => a.type === "vulnerability").length
          },
          network_analyzer: {
            accuracy: "97.8%", 
            detections: mockAlerts.filter(a => a.type === "network").length
          },
          intent_classifier: {
            accuracy: "95.4%",
            detections: mockAlerts.filter(a => a.type === "intent").length
          }
        }
        break
        
      case "stats":
        responseData.statistics = {
          total_alerts: mockAlerts.length,
          critical_alerts: mockAlerts.filter(a => a.severity === "critical").length,
          blocked_threats: mockAlerts.filter(a => a.action_taken.includes("bloqué")).length,
          active_sessions: userActivities.filter(u => !u.blocked).length,
          system_uptime: "99.98%",
          avg_response_time: "1.2s"
        }
        break
        
      case "all":
      default:
        responseData.alerts = mockAlerts
        responseData.user_activities = userActivities
        responseData.statistics = {
          total_alerts: mockAlerts.length,
          critical_alerts: mockAlerts.filter(a => a.severity === "critical").length,
          blocked_users: userActivities.filter(u => u.blocked).length,
          high_risk_users: userActivities.filter(u => u.threat_score > 0.7).length
        }
        break
    }
    
    return NextResponse.json(responseData)
  } catch (error) {
    console.error("Erreur GET admin:", error)
    return NextResponse.json(
      { error: "Erreur lors de la récupération des données" },
      { status: 500 }
    )
  }
}

// PUT - Mettre à jour les configurations
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json()
    const { config_type, settings } = body
    
    switch (config_type) {
      case "models":
        if (settings.models_status) {
          systemState.models_status = { ...systemState.models_status, ...settings.models_status }
        }
        break
        
      case "threat_level":
        if (settings.threat_level) {
          systemState.threat_level = settings.threat_level
        }
        break
        
      case "user_session":
        if (settings.session_id && settings.blocked !== undefined) {
          const userIndex = userActivities.findIndex(u => u.session_id === settings.session_id)
          if (userIndex !== -1) {
            userActivities[userIndex].blocked = settings.blocked
            if (settings.threat_score !== undefined) {
              userActivities[userIndex].threat_score = settings.threat_score
            }
          }
        }
        break
        
      default:
        return NextResponse.json(
          { error: "Type de configuration non reconnu" },
          { status: 400 }
        )
    }
    
    return NextResponse.json({
      success: true,
      message: "Configuration mise à jour",
      updated_state: systemState
    })
  } catch (error) {
    console.error("Erreur PUT admin:", error)
    return NextResponse.json(
      { error: "Erreur lors de la mise à jour" },
      { status: 500 }
    )
  }
}

// DELETE - Supprimer des alertes ou réinitialiser
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const action = searchParams.get("action")
    const alertId = searchParams.get("alert_id")
    
    switch (action) {
      case "clear_alerts":
        mockAlerts = []
        return NextResponse.json({
          success: true,
          message: "Toutes les alertes ont été supprimées"
        })
        
      case "delete_alert":
        if (alertId) {
          const initialLength = mockAlerts.length
          mockAlerts = mockAlerts.filter(alert => alert.id !== alertId)
          
          if (mockAlerts.length < initialLength) {
            return NextResponse.json({
              success: true,
              message: "Alerte supprimée avec succès"
            })
          } else {
            return NextResponse.json(
              { error: "Alerte non trouvée" },
              { status: 404 }
            )
          }
        }
        break
        
      case "reset_system":
        systemState = {
          blocked: false,
          threat_level: "safe",
          active_threats: [],
          last_scan: new Date().toISOString(),
          models_status: {
            vulnerability_classifier: "active",
            network_analyzer: "active",
            intent_classifier: "active"
          }
        }
        mockAlerts = []
        userActivities.forEach(user => {
          user.blocked = false
          user.threat_score = 0.1
        })
        
        return NextResponse.json({
          success: true,
          message: "Système réinitialisé avec succès"
        })
        
      default:
        return NextResponse.json(
          { error: "Action non reconnue" },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error("Erreur DELETE admin:", error)
    return NextResponse.json(
      { error: "Erreur lors de la suppression" },
      { status: 500 }
    )
  }
}