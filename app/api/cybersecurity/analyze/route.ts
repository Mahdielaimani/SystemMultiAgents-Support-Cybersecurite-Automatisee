// app/api/cybersecurity/analyze/route.ts
import { NextRequest, NextResponse } from "next/server"

// Interface pour typer la requête
interface SecurityAnalysisRequest {
  text: string
  models?: string[]
}

// Configuration - Utiliser les variables d'environnement Next.js
const getPythonServerUrl = () => {
  // En développement
  if (process.env.NODE_ENV === "development") {
    return "http://localhost:5000"
  }
  // En production, utiliser la variable d'environnement
  return process.env.PYTHON_SECURITY_SERVER_URL || "http://localhost:5000"
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as SecurityAnalysisRequest
    const { text, models = ["vulnerability_classifier", "network_analyzer", "intent_classifier"] } = body
    
    if (!text) {
      return NextResponse.json(
        { error: "Text is required" },
        { status: 400 }
      )
    }
    
    const pythonServerUrl = getPythonServerUrl()
    
    try {
      // Appeler le serveur Python pour l'analyse réelle
      const pythonResponse = await fetch(`${pythonServerUrl}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, models })
      })
      
      if (pythonResponse.ok) {
        const analysis = await pythonResponse.json()
        
        // Enrichir avec des métadonnées supplémentaires
        const enrichedResponse = {
          ...analysis,
          api_version: "1.0.0",
          source: "python_models"
        }
        
        // Logger les menaces détectées
        if (analysis.overall_threat_level && analysis.overall_threat_level !== "safe") {
          console.log(`🚨 Menace détectée: ${analysis.overall_threat_level}`, {
            vulnerability: analysis.vulnerability_classifier?.vulnerability_type,
            network: analysis.network_analyzer?.traffic_type,
            intent: analysis.intent_classifier?.intent
          })
        }
        
        return NextResponse.json(enrichedResponse)
      } else {
        throw new Error(`Python server error: ${pythonResponse.status}`)
      }
    } catch (pythonError) {
      console.error("Erreur serveur Python:", pythonError)
      
      // Fallback vers la simulation si le serveur Python n'est pas disponible
      console.log("⚠️ Utilisation du mode simulation (serveur Python non disponible)")
      
      const simulatedResults = await simulateAnalysis(text, models)
      return NextResponse.json({
        ...simulatedResults,
        api_version: "1.0.0",
        source: "simulation",
        warning: "Using simulated results - Python server unavailable"
      })
    }
  } catch (error) {
    console.error("Erreur API cybersécurité:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}

// Fonction de simulation pour les tests
async function simulateAnalysis(text: string, models: string[]) {
  interface SimulationResults {
    timestamp: string
    text_length: number
    models_used: string[]
    vulnerability_classifier?: {
      vulnerability_type: string
      confidence: number
    }
    network_analyzer?: {
      traffic_type: string
      confidence: number
    }
    intent_classifier?: {
      intent: string
      confidence: number
    }
    overall_threat_level?: string
  }

  const results: SimulationResults = {
    timestamp: new Date().toISOString(),
    text_length: text.length,
    models_used: models
  }
  
  // Patterns de détection pour la simulation
  const patterns = {
    xss: [/<script/i, /onerror=/i, /<iframe/i, /javascript:/i],
    sql: [/union\s+select/i, /drop\s+table/i, /or\s+1=1/i, /';/i],
    path: [/\.\.\//g, /%2e%2e/i, /etc\/passwd/i],
    network: [/ddos/i, /port\s+scan/i, /brute\s+force/i],
    malicious: [/hack/i, /exploit/i, /bypass/i, /attack/i]
  }
  
  // Utiliser Array.includes correctement
  if (models.indexOf("vulnerability_classifier") !== -1) {
    let vulnType = "SAFE"
    let confidence = 0.95
    
    if (patterns.xss.some(p => p.test(text))) {
      vulnType = "XSS"
      confidence = 0.85
    } else if (patterns.sql.some(p => p.test(text))) {
      vulnType = "SQL_INJECTION"
      confidence = 0.82
    } else if (patterns.path.some(p => p.test(text))) {
      vulnType = "PATH_TRAVERSAL"
      confidence = 0.80
    }
    
    results.vulnerability_classifier = {
      vulnerability_type: vulnType,
      confidence: confidence
    }
  }
  
  if (models.indexOf("network_analyzer") !== -1) {
    let trafficType = "NORMAL"
    let confidence = 0.90
    
    if (text.toLowerCase().indexOf("ddos") !== -1) {
      trafficType = "DDOS"
      confidence = 0.88
    } else if (text.toLowerCase().indexOf("port scan") !== -1) {
      trafficType = "PORT_SCAN"
      confidence = 0.85
    } else if (text.toLowerCase().indexOf("brute force") !== -1 || text.toLowerCase().indexOf("failed login") !== -1) {
      trafficType = "BRUTE_FORCE"
      confidence = 0.83
    }
    
    results.network_analyzer = {
      traffic_type: trafficType,
      confidence: confidence
    }
  }
  
  if (models.indexOf("intent_classifier") !== -1) {
    let intent = "Legitimate"
    let confidence = 0.80
    
    const maliciousCount = patterns.malicious.filter(p => p.test(text)).length
    
    if (maliciousCount >= 2) {
      intent = "Malicious"
      confidence = 0.75
    } else if (maliciousCount === 1) {
      intent = "Suspicious"
      confidence = 0.65
    }
    
    results.intent_classifier = {
      intent: intent,
      confidence: confidence
    }
  }
  
  // Calculer le niveau de menace global
  results.overall_threat_level = calculateThreatLevel(results)
  
  return results
}

function calculateThreatLevel(results: any): string {
  let threatScore = 0
  
  if (results.vulnerability_classifier?.vulnerability_type !== "SAFE") {
    threatScore += results.vulnerability_classifier.confidence * 3
  }
  
  if (results.network_analyzer?.traffic_type !== "NORMAL") {
    threatScore += results.network_analyzer.confidence * 2
  }
  
  if (results.intent_classifier?.intent === "Malicious") {
    threatScore += results.intent_classifier.confidence * 2.5
  } else if (results.intent_classifier?.intent === "Suspicious") {
    threatScore += results.intent_classifier.confidence * 1
  }
  
  if (threatScore >= 2.5) return "critical"
  if (threatScore >= 1.5) return "high"
  if (threatScore >= 0.5) return "medium"
  if (threatScore > 0) return "low"
  return "safe"
}

// Route pour tester la connexion au serveur Python
export async function GET() {
  const pythonServerUrl = getPythonServerUrl()
  
  try {
    const response = await fetch(`${pythonServerUrl}/health`)
    if (response.ok) {
      const health = await response.json()
      return NextResponse.json({
        status: "connected",
        python_server: pythonServerUrl,
        ...health
      })
    } else {
      throw new Error("Python server not responding")
    }
  } catch (error) {
    return NextResponse.json({
      status: "disconnected",
      python_server: pythonServerUrl,
      error: "Python server unavailable - using simulation mode"
    })
  }
}