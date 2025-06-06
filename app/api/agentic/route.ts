import { type NextRequest, NextResponse } from "next/server"

const API_BASE_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const response = await fetch(`${API_BASE_URL}/api/agentic/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error in agentic chat:", error)
    return NextResponse.json(
      {
        content: "Désolé, je rencontre un problème technique. Veuillez réessayer.",
        metadata: {
          error: error instanceof Error ? error.message : "Unknown error",
          fallback: true,
          agent_type: "networkx_hybrid",
        },
      },
      { status: 500 },
    )
  }
}

export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/agentic/health`)
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        error: error instanceof Error ? error.message : "Unknown error",
        agent: "networkx_hybrid",
      },
      { status: 500 },
    )
  }
}
