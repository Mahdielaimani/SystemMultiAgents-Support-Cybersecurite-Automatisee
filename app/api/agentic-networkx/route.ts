import { type NextRequest, NextResponse } from "next/server"
import { exec } from "child_process"
import { promisify } from "util"

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { query, session_id = "default" } = body

    if (!query) {
      return NextResponse.json({ error: "Query parameter is required" }, { status: 400 })
    }

    // Exécuter le script Python avec les paramètres
    const command = `python -c "
import sys
sys.path.append('.')
from agents.support_agent.agentic_support_agent_networkx import AgenticSupportAgentNetworkX
agent = AgenticSupportAgentNetworkX()
response = agent.process_query('${query.replace(/'/g, "\\'")}', '${session_id.replace(/'/g, "\\'")}')
confidence = agent.last_confidence_score
stats = agent.get_stats()
print('RESPONSE_START')
print(response)
print('RESPONSE_END')
print('CONFIDENCE_START')
print(confidence)
print('CONFIDENCE_END')
print('STATS_START')
import json
print(json.dumps(stats))
print('STATS_END')
"`

    const { stdout, stderr } = await execAsync(command)

    if (stderr) {
      console.error("Python error:", stderr)
    }

    // Extraire la réponse
    const responseMatch = stdout.match(/RESPONSE_START\n([\s\S]*?)\nRESPONSE_END/)
    const confidenceMatch = stdout.match(/CONFIDENCE_START\n([\s\S]*?)\nCONFIDENCE_END/)
    const statsMatch = stdout.match(/STATS_START\n([\s\S]*?)\nSTATS_END/)

    const response = responseMatch ? responseMatch[1] : "Désolé, je n'ai pas pu générer de réponse."
    const confidence = confidenceMatch ? Number.parseFloat(confidenceMatch[1]) : 0
    const stats = statsMatch ? JSON.parse(statsMatch[1]) : {}

    return NextResponse.json({
      content: response,
      metadata: {
        confidence,
        sources_count: stats.vector_hits || 0,
        graph_hits: stats.graph_hits || 0,
        memory_hits: stats.memory_hits || 0,
        response_time: stats.avg_response_time || 0,
        provider: "networkx_hybrid",
        memory_context_used: true,
        session_id,
        timestamp: new Date().toISOString(),
      },
    })
  } catch (error) {
    console.error("Error processing request:", error)
    return NextResponse.json({ error: "Failed to process request", details: (error as Error).message }, { status: 500 })
  }
}

export async function GET() {
  try {
    // Exécuter le script Python pour obtenir les statistiques
    const command = `python -c "
import sys
sys.path.append('.')
from agents.support_agent.agentic_support_agent_networkx import AgenticSupportAgentNetworkX
agent = AgenticSupportAgentNetworkX()
stats = agent.get_stats()
if hasattr(agent, 'graph_manager') and agent.graph_manager:
    graph_stats = agent.graph_manager.get_stats()
    stats['graph_stats'] = graph_stats
print('STATS_START')
import json
print(json.dumps(stats))
print('STATS_END')
"`

    const { stdout, stderr } = await execAsync(command)

    if (stderr) {
      console.error("Python error:", stderr)
    }

    // Extraire les statistiques
    const statsMatch = stdout.match(/STATS_START\n([\s\S]*?)\nSTATS_END/)
    const stats = statsMatch ? JSON.parse(statsMatch[1]) : {}

    return NextResponse.json({
      status: "healthy",
      agent: "networkx_hybrid",
      version: "1.0.0",
      stats,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error("Error getting status:", error)
    return NextResponse.json({ error: "Failed to get status", details: (error as Error).message }, { status: 500 })
  }
}
