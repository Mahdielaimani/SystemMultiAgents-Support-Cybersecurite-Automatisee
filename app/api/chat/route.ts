// app/api/chat/route.ts
import { type NextRequest, NextResponse } from "next/server"

// Configuration avec fallback robuste
const API_BASE_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Types pour les requêtes/réponses
interface ChatRequest {
  message: string
  session_id?: string
}

interface ChatResponse {
  content: string
  metadata?: {
    source?: string
    agent?: string
    confidence?: number
    provider?: string
    session_id?: string
    timestamp?: string
    [key: string]: any
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequest = await request.json()
    console.log("Frontend request received:", {
      message: body.message?.substring(0, 50) + "...",
      session_id: body.session_id
    })

    // Validation des données
    if (!body.message || typeof body.message !== 'string') {
      return NextResponse.json(
        {
          content: "Message invalide. Veuillez saisir un message valide.",
          metadata: { error: "Invalid message format", source: "validation" }
        },
        { status: 400 }
      )
    }

    // Adapter le format pour le backend
    const adaptedBody = {
      query: body.message,
      session_id: body.session_id || "default",
    }
    console.log("Sending to backend:", adaptedBody)

    // Tentative avec le backend principal
    try {
      const response = await fetch(`${API_BASE_URL}/api/agentic/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(adaptedBody),
        // Timeout pour éviter les blocages
        signal: AbortSignal.timeout(30000) // 30 secondes
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error(`Backend error: ${response.status}`, errorText)
        
        // Si le backend principal échoue, essayer l'API alternative
        return await tryFallbackAPI(adaptedBody)
      }

      const data = await response.json()
      console.log("Backend response received:", {
        content_length: data.content?.length || 0,
        has_metadata: !!data.metadata
      })

      // Vérifier que la réponse du backend contient les données attendues
      if (!data || typeof data.content === "undefined") {
        console.error("Invalid backend response:", data)
        return await tryFallbackAPI(adaptedBody)
      }

      // Retourner la réponse dans le format attendu par le frontend
      const responseData: ChatResponse = {
        content: data.content,
        metadata: {
          ...data.metadata,
          source: data.metadata?.source || "agentic_agent",
          timestamp: new Date().toISOString(),
          api_version: "1.0.0"
        }
      }

      console.log("Sending success response to frontend")
      return NextResponse.json(responseData)

    } catch (fetchError) {
      console.error("Fetch error:", fetchError)
      return await tryFallbackAPI(adaptedBody)
    }

  } catch (error) {
    console.error("Error in chat API:", error)
    return NextResponse.json(
      {
        content: "Désolé, je rencontre un problème technique. Veuillez réessayer dans quelques instants.",
        metadata: {
          error: error instanceof Error ? error.message : "Unknown error",
          source: "error_handler",
          timestamp: new Date().toISOString()
        },
      },
      { status: 500 }
    )
  }
}

// Fonction de fallback pour utiliser l'API alternative ou réponse locale
async function tryFallbackAPI(adaptedBody: { query: string; session_id: string }): Promise<NextResponse> {
  console.log("Trying fallback API...")
  
  try {
    // Essayer l'API NetworkX alternative
    const fallbackResponse = await fetch(`http://localhost:3000/api/agentic-networkx`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(adaptedBody),
      signal: AbortSignal.timeout(15000) // 15 secondes
    })

    if (fallbackResponse.ok) {
      const fallbackData = await fallbackResponse.json()
      console.log("Fallback API success")
      
      return NextResponse.json({
        content: fallbackData.content,
        metadata: {
          ...fallbackData.metadata,
          source: "fallback_api",
          fallback_used: true
        }
      })
    }
  } catch (fallbackError) {
    console.error("Fallback API also failed:", fallbackError)
  }

  // Dernière option : réponse locale basée sur des mots-clés
  return generateLocalResponse(adaptedBody.query, adaptedBody.session_id)
}

// Générateur de réponse locale
function generateLocalResponse(query: string, session_id: string): NextResponse {
  console.log("Generating local response")
  
  const queryLower = query.toLowerCase()
  let response = ""

  // Détection de mots-clés et réponses préprogrammées
  if (queryLower.includes("prix") || queryLower.includes("tarif") || queryLower.includes("coût")) {
    response = `🏷️ **Tarifs TeamSquare :**

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

Quel plan vous intéresse le plus ?`
  } 
  else if (queryLower.includes("fonctionnalité") || queryLower.includes("feature") || queryLower.includes("fonction")) {
    response = `🚀 **Fonctionnalités TeamSquare :**

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

Quelle fonctionnalité vous intéresse le plus ?`
  }
  else if (queryLower.includes("bonjour") || queryLower.includes("salut") || queryLower.includes("hello")) {
    response = "Bonjour ! 👋 Je suis l'assistant TeamSquare. Comment puis-je vous aider aujourd'hui ? Je peux vous renseigner sur nos tarifs, fonctionnalités, ou toute autre question."
  }
  else if (queryLower.includes("teamsquare") || queryLower.includes("team square")) {
    response = `**TeamSquare** est une plateforme de collaboration moderne qui aide les équipes à :

🤝 **Collaborer efficacement** avec des outils intégrés
📊 **Gérer leurs projets** de manière intuitive
💬 **Communiquer en temps réel** 
🔒 **Sécuriser leurs données** avec un niveau entreprise

Notre mission est de simplifier le travail d'équipe et d'améliorer la productivité.

Que souhaitez-vous savoir de plus ?`
  }
  else {
    response = `Merci pour votre question : "${query}"

Je suis l'assistant TeamSquare et je peux vous aider avec :
• 💰 Informations sur nos tarifs
• 🚀 Présentation des fonctionnalités
• 📞 Support technique
• 🏢 Solutions entreprise

En raison d'un problème technique temporaire, je fonctionne en mode simplifié. N'hésitez pas à reformuler votre question ou à être plus spécifique.`
  }

  return NextResponse.json({
    content: response,
    metadata: {
      source: "local_fallback",
      session_id,
      timestamp: new Date().toISOString(),
      fallback_reason: "Backend unavailable",
      local_generation: true
    }
  })
}

export async function GET() {
  try {
    // Vérifier la santé du backend
    const response = await fetch(`${API_BASE_URL}/api/agentic/health`, {
      signal: AbortSignal.timeout(5000) // 5 secondes
    })
    
    if (response.ok) {
      const data = await response.json()
      return NextResponse.json({
        status: "healthy",
        backend_status: data,
        api_base_url: API_BASE_URL
      })
    } else {
      throw new Error(`Backend health check failed: ${response.status}`)
    }
  } catch (error) {
    console.error("Health check error:", error)
    return NextResponse.json(
      {
        status: "degraded",
        error: error instanceof Error ? error.message : "Unknown error",
        fallback_available: true,
        api_base_url: API_BASE_URL
      },
      { status: 503 }
    )
  }
}