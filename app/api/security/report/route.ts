// api/security/report/route.ts
import { NextRequest, NextResponse } from 'next/server'

// Simulation de données d'alertes de sécurité
const mockSecurityAlerts = [
  {
    id: "alert_001",
    type: "vulnerability",
    severity: "critical",
    message: "Tentative d'injection SQL détectée",
    timestamp: new Date().toISOString(),
    action_taken: "Requête bloquée et IP bannie",
    source_ip: "192.168.1.100",
    user_agent: "Mozilla/5.0 (Malicious Bot)",
    details: {
      attack_vector: "SQL Injection",
      payload: "'; DROP TABLE users; --",
      affected_endpoint: "/api/user/login"
    }
  },
  {
    id: "alert_002",
    type: "network",
    severity: "high",
    message: "Trafic DDoS suspect détecté",
    timestamp: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
    action_taken: "Filtrage automatique activé",
    source_ip: "Multiple IPs",
    details: {
      request_count: 5000,
      time_window: "60 seconds",
      affected_endpoints: ["/api/*", "/login", "/register"]
    }
  },
  {
    id: "alert_003",
    type: "intent",
    severity: "medium",
    message: "Intention malveillante détectée dans le chat",
    timestamp: new Date(Date.now() - 600000).toISOString(), // 10 minutes ago
    action_taken: "Conversation surveillée et utilisateur alerté",
    source_ip: "192.168.1.55",
    details: {
      confidence_score: 0.75,
      detected_keywords: ["hack", "exploit", "vulnerability"],
      session_id: "sess_12345"
    }
  }
]

const mockSystemStats = {
  totalAlerts: 15,
  criticalAlerts: 3,
  highAlerts: 6,
  mediumAlerts: 4,
  lowAlerts: 2,
  blockedMessages: 8,
  blockedIPs: 12,
  activeSessions: 42,
  systemStatus: "warning",
  uptime: "99.8%",
  lastSecurityScan: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
  threatLevel: "medium"
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const format = searchParams.get('format') || 'json'
    const detailed = searchParams.get('detailed') === 'true'

    // Générer le rapport complet
    const report = {
      metadata: {
        report_id: `SEC_RPT_${Date.now()}`,
        generated_at: new Date().toISOString(),
        generated_by: "Security Admin System",
        report_type: detailed ? "detailed" : "summary",
        version: "1.0.0"
      },
      executive_summary: {
        period: "Last 24 hours",
        total_incidents: mockSecurityAlerts.length,
        critical_incidents: mockSecurityAlerts.filter(a => a.severity === "critical").length,
        security_score: 85,
        overall_status: mockSystemStats.systemStatus,
        key_findings: [
          "1 critical SQL injection attempt blocked",
          "DDoS attack successfully mitigated",
          "3 suspicious chat interactions monitored",
          "System security posture: GOOD"
        ]
      },
      system_statistics: mockSystemStats,
      security_alerts: detailed ? mockSecurityAlerts : mockSecurityAlerts.slice(0, 5),
      threat_analysis: {
        current_threat_level: mockSystemStats.threatLevel,
        top_attack_vectors: [
          { type: "SQL Injection", count: 5, trend: "increasing" },
          { type: "DDoS", count: 3, trend: "stable" },
          { type: "Malicious Chat", count: 8, trend: "decreasing" }
        ],
        geographic_distribution: [
          { country: "Unknown", percentage: 40 },
          { country: "Russia", percentage: 25 },
          { country: "China", percentage: 20 },
          { country: "USA", percentage: 15 }
        ]
      },
      recommendations: [
        {
          priority: "high",
          title: "Strengthen SQL Injection Protection",
          description: "Implement additional parameterized query validation",
          estimated_effort: "2-3 days",
          risk_reduction: "high"
        },
        {
          priority: "medium",
          title: "Enhance DDoS Mitigation",
          description: "Configure advanced rate limiting rules",
          estimated_effort: "1 day",
          risk_reduction: "medium"
        },
        {
          priority: "low",
          title: "User Security Training",
          description: "Conduct security awareness sessions",
          estimated_effort: "1 week",
          risk_reduction: "low"
        }
      ],
      compliance_status: {
        gdpr_compliant: true,
        iso27001_compliant: true,
        last_audit: "2024-05-15",
        next_audit: "2024-08-15"
      }
    }

    // Retourner selon le format demandé
    if (format === 'pdf') {
      // En production, vous généreriez un vrai PDF
      return new NextResponse(
        JSON.stringify({ 
          message: "PDF generation not implemented in demo",
          download_url: "/api/security/report?format=json" 
        }),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    return new NextResponse(JSON.stringify(report, null, 2), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Content-Disposition': `attachment; filename="security-report-${new Date().toISOString().split('T')[0]}.json"`
      }
    })

  } catch (error) {
    console.error('Erreur génération rapport:', error)
    return new NextResponse(
      JSON.stringify({ error: 'Erreur lors de la génération du rapport' }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { 
      start_date, 
      end_date, 
      severity_filter, 
      include_recommendations,
      format = 'json' 
    } = body

    // Filtrer les alertes selon les critères
    let filteredAlerts = mockSecurityAlerts

    if (severity_filter && severity_filter.length > 0) {
      filteredAlerts = filteredAlerts.filter(alert => 
        severity_filter.includes(alert.severity)
      )
    }

    if (start_date) {
      filteredAlerts = filteredAlerts.filter(alert => 
        new Date(alert.timestamp) >= new Date(start_date)
      )
    }

    if (end_date) {
      filteredAlerts = filteredAlerts.filter(alert => 
        new Date(alert.timestamp) <= new Date(end_date)
      )
    }

    const customReport = {
      metadata: {
        report_id: `SEC_CUSTOM_${Date.now()}`,
        generated_at: new Date().toISOString(),
        filters_applied: {
          start_date,
          end_date,
          severity_filter,
          include_recommendations
        }
      },
      summary: {
        total_alerts: filteredAlerts.length,
        period: start_date && end_date ? 
          `${start_date} to ${end_date}` : 
          "Custom filtered period"
      },
      alerts: filteredAlerts,
      statistics: {
        by_severity: {
          critical: filteredAlerts.filter(a => a.severity === "critical").length,
          high: filteredAlerts.filter(a => a.severity === "high").length,
          medium: filteredAlerts.filter(a => a.severity === "medium").length,
          low: filteredAlerts.filter(a => a.severity === "low").length
        },
        by_type: {
          vulnerability: filteredAlerts.filter(a => a.type === "vulnerability").length,
          network: filteredAlerts.filter(a => a.type === "network").length,
          intent: filteredAlerts.filter(a => a.type === "intent").length
        }
      }
    }

    if (include_recommendations) {
      customReport.recommendations = [
        {
          title: "Automated Response Enhancement",
          description: "Based on filtered data, consider implementing automated responses for recurring threat patterns"
        }
      ]
    }

    return new NextResponse(JSON.stringify(customReport, null, 2), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Content-Disposition': `attachment; filename="custom-security-report-${Date.now()}.json"`
      }
    })

  } catch (error) {
    console.error('Erreur rapport personnalisé:', error)
    return new NextResponse(
      JSON.stringify({ error: 'Erreur lors de la génération du rapport personnalisé' }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}