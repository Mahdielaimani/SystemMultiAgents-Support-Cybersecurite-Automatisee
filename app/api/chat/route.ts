import { type NextRequest, NextResponse } from "next/server"

const API_BASE_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log("Frontend request:", body)

    // Adapter le format pour le backend
    const adaptedBody = {
      query: body.message,
      session_id: body.session_id || "default",
    }
    console.log("Sending to backend:", adaptedBody)

    const response = await fetch(`${API_BASE_URL}/api/agentic/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(adaptedBody),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`Backend error: ${response.status}`, errorText)
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    console.log("Backend response received:", data)

    // Vérifier que la réponse du backend contient les données attendues
    if (!data || typeof data.content === "undefined") {
      console.error("Invalid backend response:", data)
      throw new Error("Backend response missing content")
    }

    // Retourner la réponse dans le format attendu par le frontend
    const responseData = {
      content: data.content,
      metadata: data.metadata || {},
    }

    console.log("Sending to frontend:", responseData)
    return NextResponse.json(responseData)
  } catch (error) {
    console.error("Error in chat API:", error)
    return NextResponse.json(
      {
        content: "Désolé, je rencontre un problème technique. Veuillez réessayer.",
        metadata: {
          error: error instanceof Error ? error.message : "Unknown error",
          source: "error",
        },
      },
      { status: 500 },
    )
  }
}

export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/agentic/health`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}
