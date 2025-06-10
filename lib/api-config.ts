// lib/api-config.ts
/**
 * Configuration centralisée pour les appels API
 */

export interface ApiConfig {
  baseUrl: string
  timeout: number
  retries: number
  retryDelay: number
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  source: 'backend' | 'fallback' | 'local'
  timestamp: string
}

// Configuration par défaut
export const DEFAULT_API_CONFIG: ApiConfig = {
  baseUrl: process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 30000, // 30 secondes
  retries: 2,
  retryDelay: 1000 // 1 seconde
}

// URLs des endpoints
export const API_ENDPOINTS = {
  CHAT: "/api/agentic/chat",
  HEALTH: "/api/agentic/health",
  STATUS: "/api/agentic/status",
  SECURITY_ANALYZE: "/api/cybersecurity/analyze",
  SECURITY_HEALTH: "/api/cybersecurity/health",
  SECURITY_ALERTS: "/api/cybersecurity/alerts"
} as const

/**
 * Fonction utilitaire pour faire des appels API avec retry et fallback
 */
export async function apiCall<T = any>(
  endpoint: string,
  options: RequestInit = {},
  config: Partial<ApiConfig> = {}
): Promise<ApiResponse<T>> {
  const finalConfig = { ...DEFAULT_API_CONFIG, ...config }
  const url = `${finalConfig.baseUrl}${endpoint}`
  
  // Configuration de la requête avec timeout
  const requestOptions: RequestInit = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...options.headers
    },
    signal: AbortSignal.timeout(finalConfig.timeout)
  }

  let lastError: Error | null = null

  // Tentatives avec retry
  for (let attempt = 0; attempt <= finalConfig.retries; attempt++) {
    try {
      console.log(`API Call attempt ${attempt + 1}/${finalConfig.retries + 1}: ${endpoint}`)
      
      const response = await fetch(url, requestOptions)
      
      if (response.ok) {
        const data = await response.json()
        return {
          success: true,
          data,
          source: 'backend',
          timestamp: new Date().toISOString()
        }
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error))
      console.warn(`API call attempt ${attempt + 1} failed:`, lastError.message)
      
      // Attendre avant la prochaine tentative (sauf pour la dernière)
      if (attempt < finalConfig.retries) {
        await new Promise(resolve => setTimeout(resolve, finalConfig.retryDelay))
      }
    }
  }

  // Toutes les tentatives ont échoué
  return {
    success: false,
    error: lastError?.message || "Unknown error",
    source: 'backend',
    timestamp: new Date().toISOString()
  }
}

/**
 * Fonction spécialisée pour les appels de chat
 */
export async function chatApiCall(message: string, sessionId: string = "default"): Promise<ApiResponse> {
  const response = await apiCall(API_ENDPOINTS.CHAT, {
    method: "POST",
    body: JSON.stringify({
      query: message,
      session_id: sessionId
    })
  })

  // Si l'API backend échoue, essayer l'API alternative
  if (!response.success) {
    console.log("Backend failed, trying alternative API...")
    
    try {
      const fallbackResponse = await fetch("/api/agentic-networkx", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: message,
          session_id: sessionId
        }),
        signal: AbortSignal.timeout(15000)
      })

      if (fallbackResponse.ok) {
        const data = await fallbackResponse.json()
        return {
          success: true,
          data,
          source: 'fallback',
          timestamp: new Date().toISOString()
        }
      }
    } catch (fallbackError) {
      console.error("Fallback API also failed:", fallbackError)
    }

    // Dernière option : réponse locale
    return {
      success: true,
      data: generateLocalChatResponse(message, sessionId),
      source: 'local',
      timestamp: new Date().toISOString()
    }
  }

  return response
}

/**
 * Générateur de réponse locale en cas d'échec de toutes les APIs
 */
function generateLocalChatResponse(message: string, sessionId: string) {
  const messageLower = message.toLowerCase()
  
  let content = ""

  if (messageLower.includes("prix") || messageLower.includes("tarif")) {
    content = `🏷️ **Tarifs TeamSquare :**

💰 **Starter** : 9€/mois par utilisateur
💰 **Professional** : 19€/mois par utilisateur  
💰 **Enterprise** : Sur devis

Quel plan vous intéresse ?`
  } else if (messageLower.includes("fonctionnalité") || messageLower.includes("feature")) {
    content = `🚀 **Fonctionnalités TeamSquare :**

• Chat en temps réel
• Gestion de projets
• Partage de fichiers
• Visioconférences intégrées

Que souhaitez-vous savoir de plus ?`
  } else if (messageLower.includes("bonjour") || messageLower.includes("hello")) {
    content = "Bonjour ! Je suis l'assistant TeamSquare. Comment puis-je vous aider ?"
  } else {
    content = `Merci pour votre question. En raison d'un problème technique temporaire, je fonctionne en mode simplifié. 

Je peux vous aider avec :
• Informations sur nos tarifs
• Présentation des fonctionnalités  
• Support général

N'hésitez pas à reformuler votre question.`
  }

  return {
    content,
    metadata: {
      source: "local_generator",
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      fallback_reason: "All APIs unavailable"
    }
  }
}

/**
 * Fonction pour vérifier la santé de l'API
 */
export async function checkApiHealth(): Promise<{
  backend: boolean
  fallback: boolean
  timestamp: string
}> {
  const results = {
    backend: false,
    fallback: false,
    timestamp: new Date().toISOString()
  }

  // Vérifier le backend principal
  try {
    const backendResponse = await fetch(`${DEFAULT_API_CONFIG.baseUrl}${API_ENDPOINTS.HEALTH}`, {
      signal: AbortSignal.timeout(5000)
    })
    results.backend = backendResponse.ok
  } catch {
    results.backend = false
  }

  // Vérifier l'API de fallback
  try {
    const fallbackResponse = await fetch("/api/agentic-networkx", {
      method: "GET",
      signal: AbortSignal.timeout(5000)
    })
    results.fallback = fallbackResponse.ok
  } catch {
    results.fallback = false
  }

  return results
}