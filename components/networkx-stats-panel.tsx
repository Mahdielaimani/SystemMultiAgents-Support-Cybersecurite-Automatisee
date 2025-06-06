"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { Database, Network, Brain, Zap, Clock, MessageSquare } from "lucide-react"

interface NetworkXStats {
  total_queries: number
  vector_hits: number
  graph_hits: number
  memory_hits: number
  avg_confidence: number
  avg_response_time: number
  memory_sessions: number
  components_status: {
    llm_manager: boolean
    embedding_model: boolean
    chromadb: boolean
    networkx_graph: boolean
  }
  graph_stats?: {
    entities_count: number
    relations_count: number
    nodes_count: number
    edges_count: number
    entity_types: string[]
    relation_types: string[]
    is_connected: boolean
  }
}

export default function NetworkXStatsPanel() {
  const [stats, setStats] = useState<NetworkXStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const response = await fetch("/api/agentic-networkx")

        if (!response.ok) {
          throw new Error(`Erreur: ${response.status}`)
        }

        const data = await response.json()
        setStats(data.stats)
        setError(null)
      } catch (err) {
        setError((err as Error).message || "Erreur lors de la récupération des statistiques")
        console.error("Erreur:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()

    // Rafraîchir toutes les 30 secondes
    const interval = setInterval(fetchStats, 30000)

    return () => clearInterval(interval)
  }, [])

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return "text-green-600"
    if (confidence >= 0.4) return "text-yellow-600"
    return "text-red-600"
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5 text-purple-600" />
            Statistiques NetworkX
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-40">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5 text-red-600" />
            Erreur
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-red-500">{error}</div>
        </CardContent>
      </Card>
    )
  }

  if (!stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5 text-purple-600" />
            Statistiques NetworkX
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-gray-500">Aucune donnée disponible</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Network className="h-5 w-5 text-purple-600" />
          Statistiques NetworkX
        </CardTitle>
        <CardDescription>RAG Hybride avec Vector + NetworkX Graph</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm flex items-center gap-1">
                <Database className="h-4 w-4" />
                Requêtes
              </span>
              <Badge variant="outline">{stats.total_queries}</Badge>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm flex items-center gap-1">
                <Zap className="h-4 w-4" />
                Vector Hits
              </span>
              <Badge variant="default">{stats.vector_hits}</Badge>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm flex items-center gap-1">
                <Network className="h-4 w-4" />
                Graph Hits
              </span>
              <Badge variant="secondary">{stats.graph_hits}</Badge>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm flex items-center gap-1">
                <Brain className="h-4 w-4" />
                Memory Hits
              </span>
              <Badge variant="outline">{stats.memory_hits}</Badge>
            </div>
          </div>

          <div className="space-y-2">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Confiance Moy.</span>
                <span className={`text-sm font-medium ${getConfidenceColor(stats.avg_confidence)}`}>
                  {(stats.avg_confidence * 100).toFixed(1)}%
                </span>
              </div>
              <Progress value={stats.avg_confidence * 100} className="h-2" />
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm flex items-center gap-1">
                <Clock className="h-4 w-4" />
                Temps Moy.
              </span>
              <span className="text-sm font-medium">{stats.avg_response_time.toFixed(1)}s</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm flex items-center gap-1">
                <MessageSquare className="h-4 w-4" />
                Sessions
              </span>
              <Badge variant="outline">{stats.memory_sessions}</Badge>
            </div>
          </div>
        </div>

        <Separator />

        <div className="space-y-2">
          <h4 className="text-sm font-medium">État des composants</h4>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${stats.components_status.llm_manager ? "bg-green-500" : "bg-red-500"}`}
              ></div>
              <span className="text-xs">LLM Manager</span>
            </div>
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${stats.components_status.embedding_model ? "bg-green-500" : "bg-red-500"}`}
              ></div>
              <span className="text-xs">Embedding Model</span>
            </div>
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${stats.components_status.chromadb ? "bg-green-500" : "bg-red-500"}`}
              ></div>
              <span className="text-xs">ChromaDB</span>
            </div>
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${stats.components_status.networkx_graph ? "bg-green-500" : "bg-red-500"}`}
              ></div>
              <span className="text-xs">NetworkX Graph</span>
            </div>
          </div>
        </div>

        {stats.graph_stats && (
          <>
            <Separator />
            <div className="space-y-2">
              <h4 className="text-sm font-medium flex items-center gap-1">
                <Network className="h-4 w-4" />
                Statistiques du Graphe
              </h4>
              <div className="grid grid-cols-2 gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs">Entités</span>
                  <Badge variant="outline" className="text-xs">
                    {stats.graph_stats.entities_count}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs">Relations</span>
                  <Badge variant="outline" className="text-xs">
                    {stats.graph_stats.relations_count}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs">Types d'entités</span>
                  <Badge variant="outline" className="text-xs">
                    {stats.graph_stats.entity_types.length}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs">Types de relations</span>
                  <Badge variant="outline" className="text-xs">
                    {stats.graph_stats.relation_types.length}
                  </Badge>
                </div>
                <div className="flex items-center justify-between col-span-2">
                  <span className="text-xs">Graphe connecté</span>
                  <Badge variant={stats.graph_stats.is_connected ? "default" : "destructive"} className="text-xs">
                    {stats.graph_stats.is_connected ? "Oui" : "Non"}
                  </Badge>
                </div>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
