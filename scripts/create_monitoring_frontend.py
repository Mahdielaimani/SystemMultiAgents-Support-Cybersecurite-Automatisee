#!/usr/bin/env python3
"""
Créer le frontend de monitoring pour le robot gardien
"""
import os
from pathlib import Path

def create_monitoring_frontend():
    """Créer l'interface de monitoring du robot gardien"""
    
    # Composant de monitoring
    monitoring_content = '''
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Shield, AlertTriangle, CheckCircle, XCircle, Activity, Globe, Scan, BotIcon as Robot, Zap, Eye, Clock, TrendingUp } from 'lucide-react'

interface GuardianStatus {
  name: string
  status: string
  running: boolean
  websites_guarded: number
  total_scans: number
  stats: {
    total_scans: number
    vulnerabilities_found: number
    high_risk: number
    medium_risk: number
    low_risk: number
  }
  last_update: string
}

interface RealtimeData {
  guardian_status: string
  websites_monitored: number
  recent_scans: Array<{
    id: string
    website: string
    timestamp: string
    risk_level: string
    vulnerabilities_count: number
  }>
  vulnerability_stats: {
    total_scans: number
    vulnerabilities_found: number
    high_risk: number
    medium_risk: number
    low_risk: number
  }
  active_threats: Array<any>
}

export function GuardianMonitoring() {
  const [guardianStatus, setGuardianStatus] = useState<GuardianStatus | null>(null)
  const [realtimeData, setRealtimeData] = useState<RealtimeData | null>(null)
  const [newWebsite, setNewWebsite] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  // Récupérer les données en temps réel
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Statut du gardien
        const statusResponse = await fetch("/api/guardian/status")
        if (statusResponse.ok) {
          const status = await statusResponse.json()
          setGuardianStatus(status)
        }

        // Données temps réel
        const realtimeResponse = await fetch("/api/guardian/realtime")
        if (realtimeResponse.ok) {
          const realtime = await realtimeResponse.json()
          setRealtimeData(realtime)
        }
      } catch (error) {
        console.error("Erreur récupération données:", error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000) // Mise à jour toutes les 5 secondes

    return () => clearInterval(interval)
  }, [])

  const startGuardian = async () => {
    setIsLoading(true)
    try {
      await fetch("/api/guardian/start", { method: "POST" })
    } catch (error) {
      console.error("Erreur démarrage gardien:", error)
    }
    setIsLoading(false)
  }

  const stopGuardian = async () => {
    setIsLoading(true)
    try {
      await fetch("/api/guardian/stop", { method: "POST" })
    } catch (error) {
      console.error("Erreur arrêt gardien:", error)
    }
    setIsLoading(false)
  }

  const addWebsite = async () => {
    if (!newWebsite.trim()) return

    setIsLoading(true)
    try {
      await fetch("/api/guardian/add-website", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: newWebsite, scan_depth: 2 })
      })
      setNewWebsite("")
    } catch (error) {
      console.error("Erreur ajout site:", error)
    }
    setIsLoading(false)
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "critical": return "bg-red-500"
      case "high": return "bg-orange-500"
      case "medium": return "bg-yellow-500"
      case "low": return "bg-green-500"
      default: return "bg-gray-500"
    }
  }

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case "critical": return <XCircle className="w-4 h-4" />
      case "high": return <AlertTriangle className="w-4 h-4" />
      case "medium": return <Eye className="w-4 h-4" />
      case "low": return <CheckCircle className="w-4 h-4" />
      default: return <Activity className="w-4 h-4" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6">
      {/* En-tête */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
                <Robot className="w-8 h-8 text-white" />
                {guardianStatus?.running && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-pulse" />
                )}
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Guardian Robot
              </h1>
              <p className="text-slate-400">Cybersecurity Monitoring System</p>
            </div>
          </div>
          
          <div className="flex gap-3">
            <Button
              onClick={startGuardian}
              disabled={isLoading || guardianStatus?.running}
              className="bg-green-600 hover:bg-green-700"
            >
              <Zap className="w-4 h-4 mr-2" />
              Start Guardian
            </Button>
            <Button
              onClick={stopGuardian}
              disabled={isLoading || !guardianStatus?.running}
              variant="destructive"
            >
              <XCircle className="w-4 h-4 mr-2" />
              Stop Guardian
            </Button>
          </div>
        </div>
      </div>

      {/* Statistiques principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Sites Surveillés</p>
                <p className="text-2xl font-bold text-white">
                  {realtimeData?.websites_monitored || 0}
                </p>
              </div>
              <Globe className="w-8 h-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Scans Totaux</p>
                <p className="text-2xl font-bold text-white">
                  {realtimeData?.vulnerability_stats?.total_scans || 0}
                </p>
              </div>
              <Scan className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Vulnérabilités</p>
                <p className="text-2xl font-bold text-white">
                  {realtimeData?.vulnerability_stats?.vulnerabilities_found || 0}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-orange-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Menaces Actives</p>
                <p className="text-2xl font-bold text-white">
                  {realtimeData?.active_threats?.length || 0}
                </p>
              </div>
              <Shield className="w-8 h-8 text-red-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Statut du Guardian */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Robot className="w-5 h-5" />
              Statut du Guardian
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">État</span>
                <Badge 
                  className={`${
                    guardianStatus?.running 
                      ? "bg-green-600 text-white" 
                      : "bg-red-600 text-white"
                  }`}
                >
                  {guardianStatus?.running ? "ACTIF" : "ARRÊTÉ"}
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Dernière mise à jour</span>
                <span className="text-white text-sm">
                  {guardianStatus?.last_update 
                    ? new Date(guardianStatus.last_update).toLocaleTimeString()
                    : "N/A"
                  }
                </span>
              </div>

              {/* Répartition des vulnérabilités */}
              <div className="space-y-2">
                <p className="text-slate-400 text-sm">Répartition des risques</p>
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-red-600/20 p-2 rounded text-center">
                    <p className="text-red-400 text-xs">Élevé</p>
                    <p className="text-white font-bold">
                      {realtimeData?.vulnerability_stats?.high_risk || 0}
                    </p>
                  </div>
                  <div className="bg-yellow-600/20 p-2 rounded text-center">
                    <p className="text-yellow-400 text-xs">Moyen</p>
                    <p className="text-white font-bold">
                      {realtimeData?.vulnerability_stats?.medium_risk || 0}
                    </p>
                  </div>
                  <div className="bg-green-600/20 p-2 rounded text-center">
                    <p className="text-green-400 text-xs">Faible</p>
                    <p className="text-white font-bold">
                      {realtimeData?.vulnerability_stats?.low_risk || 0}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Ajouter un site */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5" />
              Ajouter un Site à Surveiller
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={newWebsite}
                  onChange={(e) => setNewWebsite(e.target.value)}
                  placeholder="https://example.com"
                  className="bg-slate-700 border-slate-600 text-white"
                />
                <Button 
                  onClick={addWebsite}
                  disabled={isLoading || !newWebsite.trim()}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  Ajouter
                </Button>
              </div>
              <p className="text-slate-400 text-sm">
                Le robot gardien surveillera automatiquement ce site toutes les 5 minutes.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Scans récents */}
      <Card className="bg-slate-800/50 border-slate-700 mt-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Scans Récents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-64">
            <div className="space-y-3">
              {realtimeData?.recent_scans?.map((scan) => (
                <div 
                  key={scan.id}
                  className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${getRiskColor(scan.risk_level)}`} />
                    <div>
                      <p className="text-white font-medium">{scan.website}</p>
                      <p className="text-slate-400 text-sm">
                        {new Date(scan.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-white border-slate-600">
                      {scan.vulnerabilities_count} vulnérabilités
                    </Badge>
                    {getRiskIcon(scan.risk_level)}
                  </div>
                </div>
              ))}
              
              {(!realtimeData?.recent_scans || realtimeData.recent_scans.length === 0) && (
                <div className="text-center py-8 text-slate-400">
                  <Scan className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Aucun scan récent</p>
                  <p className="text-sm">Le robot gardien n\\'a pas encore effectué de scan.</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}
'''
    
    # Sauvegarder le composant
    component_file = Path("components/guardian-monitoring.tsx")
    component_file.parent.mkdir(parents=True, exist_ok=True)
    component_file.write_text(monitoring_content)
    
    print("✅ Frontend de monitoring créé")

def main():
    print("🖥️ CRÉATION DU FRONTEND DE MONITORING")
    print("=" * 60)
    
    create_monitoring_frontend()
    
    print("\n✅ FRONTEND DE MONITORING CRÉÉ")
    print("=" * 60)
    print("🖥️ Interface de monitoring en temps réel créée")
    print("- ✅ Statut du robot gardien")
    print("- ✅ Statistiques en temps réel")
    print("- ✅ Scans récents")
    print("- ✅ Gestion des sites surveillés")

if __name__ == "__main__":
    main()
