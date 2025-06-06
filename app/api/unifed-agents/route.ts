import { type NextRequest, NextResponse } from "next/server"

// Types pour les requêtes
interface UnifiedAgentRequest {
  query: string
  agent_type: "support" | "security" | "auto"
  session_id?: string
  target?: string
  scan_type?: string
}

// Simuler les réponses des agents
function getAgentResponse(query: string, agentType: "support" | "security"): any {
  if (agentType === "support") {
    if (query.toLowerCase().includes("prix") || query.toLowerCase().includes("tarif")) {
      return {
        response: `🏷️ **Tarifs TeamSquare :**

💰 **Starter** : 9€/mois par utilisateur
   • Jusqu'à 10 utilisateurs
   • 5GB de stockage
   • Support email

💰 **Professional** : 19€/mois par utilisateur  
   • Utilisateurs illimités
   • 100GB de stockage
   • Support prioritaire

💰 **Enterprise** : Sur devis
   • Tout du plan Pro
   • Stockage illimité
   • Support dédié

Lequel vous intéresse le plus ?`,
        metadata: {
          agent: "support",
          confidence: 0.95,
          source: "pricing_database",
        },
      }
    } else if (query.toLowerCase().includes("fonctionnalité") || query.toLowerCase().includes("feature")) {
      return {
        response: `🚀 **Fonctionnalités TeamSquare :**

**Collaboration :**
• Chat en temps réel
• Partage de fichiers sécurisé
• Espaces de travail collaboratifs

**Gestion de projet :**
• Suivi des tâches
• Planification d'équipe
• Rapports de progression

**Communication :**
• Visioconférences intégrées
• Notifications intelligentes

Quelle fonctionnalité vous intéresse le plus ?`,
        metadata: {
          agent: "support",
          confidence: 0.92,
          source: "features_database",
        },
      }
    } else {
      return {
        response:
          "Bonjour ! 👋 Je suis l'assistant TeamSquare. Je peux vous aider avec nos tarifs, fonctionnalités, ou toute question sur notre plateforme de collaboration. Comment puis-je vous aider ?",
        metadata: {
          agent: "support",
          confidence: 0.85,
          source: "general_support",
        },
      }
    }
  } else {
    // Agent de sécurité
    if (query.toLowerCase().includes("scan") || query.toLowerCase().includes("analyser")) {
      return {
        response: `🔒 **Analyse de sécurité initiée**

🔍 **Scan en cours...**
• Vérification des en-têtes HTTP
• Analyse des vulnérabilités communes
• Test de configuration SSL/TLS

**Résultats préliminaires :**
• ✅ Certificat SSL valide
• ⚠️ En-tête CSP manquant
• ⚠️ X-Frame-Options non configuré

Voulez-vous un rapport détaillé ?`,
        metadata: {
          agent: "security",
          confidence: 0.88,
          scan_id: `scan_${Date.now()}`,
          vulnerabilities_found: 2,
        },
      }
    } else if (query.toLowerCase().includes("vulnérabilité") || query.toLowerCase().includes("vulnerability")) {
      return {
        response: `🛡️ **Analyse des vulnérabilités**

**Types de vulnérabilités détectables :**
• Injections SQL
• Cross-Site Scripting (XSS)
• Cross-Site Request Forgery (CSRF)
• Configurations non sécurisées
• Fuites d'informations

**Recommandations :**
• Effectuer des scans réguliers
• Maintenir les systèmes à jour
• Implémenter des en-têtes de sécurité

Souhaitez-vous analyser une URL spécifique ?`,
        metadata: {
          agent: "security",
          confidence: 0.9,
          source: "vulnerability_database",
        },
      }
    } else {
      return {
        response: `🛡️ **Agent de Cybersécurité NextGen**

Je peux vous aider avec :
• 🔍 Scans de sécurité d'URLs
• 🚨 Détection de vulnérabilités
• 📊 Analyse du trafic réseau
• 📋 Génération de rapports de sécurité
• 💡 Recommandations de sécurité

Que souhaitez-vous analyser aujourd'hui ?`,
        metadata: {
          agent: "security",
          confidence: 0.85,
          capabilities: ["web_scanning", "vulnerability_detection", "network_analysis"],
        },
      }
    }
  }
}

// Fonction pour déterminer automatiquement l'agent
function determineAgent(query: string): "support" | "security" {
  const securityKeywords = [
    "sécurité",
    "security",
    "scan",
    "vulnérabilité",
    "vulnerability",
    "hack",
    "attaque",
    "malware",
    "virus",
    "firewall",
    "ssl",
    "https",
    "analyse",
    "audit",
    "pentest",
    "threat",
    "menace",
  ]

  const supportKeywords = [
    "prix",
    "tarif",
    "price",
    "fonctionnalité",
    "feature",
    "aide",
    "help",
    "teamsquare",
    "collaboration",
    "équipe",
    "team",
    "projet",
    "project",
    "comment",
    "pourquoi",
    "installation",
    "configuration",
  ]

  const queryLower = query.toLowerCase()

  const securityScore = securityKeywords.filter((keyword) => queryLower.includes(keyword)).length
  const supportScore = supportKeywords.filter((keyword) => queryLower.includes(keyword)).length

  return securityScore > supportScore ? "security" : "support"
}

export async function POST(request: NextRequest) {
  try {
    const body: UnifiedAgentRequest = await request.json()
    const { query, agent_type, session_id = "default", target, scan_type } = body

    // Déterminer l'agent à utiliser
    let selectedAgent = agent_type
    if (agent_type === "auto") {
      selectedAgent = determineAgent(query)
    }

    // Simuler un délai de traitement
    await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 2000))

    // Obtenir la réponse de l'agent approprié
    const agentResponse = getAgentResponse(query, selectedAgent as "support" | "security")

    // Ajouter des métadonnées supplémentaires
    const response = {
      ...agentResponse,
      metadata: {
        ...agentResponse.metadata,
        session_id,
        timestamp: new Date().toISOString(),
        processing_time: Math.random() * 2 + 0.5,
        selected_agent: selectedAgent,
        auto_selected: agent_type === "auto",
      },
    }

    return NextResponse.json(response)
  } catch (error) {
    console.error("Erreur API agents unifiés:", error)
    return NextResponse.json(
      {
        error: "Erreur interne du serveur",
        response: "Désolé, une erreur s'est produite. Veuillez réessayer.",
        metadata: {
          error: true,
          timestamp: new Date().toISOString(),
        },
      },
      { status: 500 },
    )
  }
}

export async function GET() {
  return NextResponse.json({
    status: "healthy",
    agents: {
      support: {
        name: "TeamSquare Support Agent",
        version: "2.0.0",
        capabilities: ["customer_support", "pricing_info", "feature_explanation"],
      },
      security: {
        name: "Cybersecurity Agent",
        version: "2.0.0",
        capabilities: ["web_scanning", "vulnerability_detection", "security_analysis"],
      },
    },
    features: ["auto_agent_selection", "unified_interface", "real_time_analysis"],
    timestamp: new Date().toISOString(),
  })
}
