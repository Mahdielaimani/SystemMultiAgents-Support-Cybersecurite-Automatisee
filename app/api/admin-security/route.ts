// app/api/admin-security/route.ts
import { NextRequest, NextResponse } from 'next/server'

// URL du serveur FastAPI
const FASTAPI_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// GET - Proxy vers FastAPI
export async function GET(request: NextRequest) {
  try {
    // Récupérer les paramètres de requête
    const searchParams = request.nextUrl.searchParams
    const queryString = searchParams.toString()
    
    // Faire un proxy vers le vrai serveur FastAPI
    const response = await fetch(
      `${FASTAPI_URL}/api/admin-security${queryString ? `?${queryString}` : ''}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        // Important : ne pas mettre de cache pour avoir les données en temps réel
        cache: 'no-store'
      }
    )

    if (!response.ok) {
      throw new Error(`FastAPI responded with status: ${response.status}`)
    }

    const data = await response.json()
    
    // Assurer que models_status existe toujours
    if (data.system_state && !data.system_state.models_status) {
      data.system_state.models_status = {
        vulnerability_classifier: "active",
        network_analyzer: "active",
        intent_classifier: "active"
      }
    }
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying to FastAPI:', error)
    
    // En cas d'erreur de connexion, renvoyer un état vide
    // PAS DE DONNÉES MOCKÉES !
    return NextResponse.json({
      system_state: {
        blocked: false,
        threat_level: "safe",
        block_reason: null,
        last_block_time: null,
        active_sessions: {},
        total_threats_detected: 0,
        last_scan: new Date().toISOString(),
        active_threats: [],
        models_status: {
          vulnerability_classifier: "inactive",
          network_analyzer: "inactive",
          intent_classifier: "inactive"
        }
      },
      alerts: [],  // Vide !
      user_activities: [],  // Vide !
      timestamp: new Date().toISOString(),
      error: "FastAPI server not available",
      fastapi_url: FASTAPI_URL
    })
  }
}

// POST - Proxy vers FastAPI
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Faire un proxy vers le vrai serveur FastAPI
    const response = await fetch(`${FASTAPI_URL}/api/admin-security`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        errorData || { error: `FastAPI responded with status: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    // Assurer que models_status existe dans la réponse si system_state est présent
    if (data.system_state && !data.system_state.models_status) {
      data.system_state.models_status = {
        vulnerability_classifier: "active",
        network_analyzer: "active",
        intent_classifier: "active"
      }
    }
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying POST to FastAPI:', error)
    
    return NextResponse.json(
      { error: 'Failed to connect to security API' },
      { status: 500 }
    )
  }
}

// PUT - Proxy vers FastAPI (si nécessaire)
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${FASTAPI_URL}/api/admin-security`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        errorData || { error: `FastAPI responded with status: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying PUT to FastAPI:', error)
    
    return NextResponse.json(
      { error: 'Failed to connect to security API' },
      { status: 500 }
    )
  }
}

// DELETE - Proxy vers FastAPI (si nécessaire)
export async function DELETE(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const queryString = searchParams.toString()
    
    const response = await fetch(
      `${FASTAPI_URL}/api/admin-security${queryString ? `?${queryString}` : ''}`,
      {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      }
    )

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        errorData || { error: `FastAPI responded with status: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying DELETE to FastAPI:', error)
    
    return NextResponse.json(
      { error: 'Failed to connect to security API' },
      { status: 500 }
    )
  }
}