"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Bot, Shield, MessageSquare, Activity, Zap, BarChart3, Settings } from "lucide-react"

export function AgentsDashboard() {
  const [activeAgents, setActiveAgents] = useState([
    {
      id: "support",
      name: "Support Agent",
      type: "Customer Support",
      status: "active",
      icon: MessageSquare,
      color: "from-green-500 to-teal-600",
      performance: 98,
      tasks: 1247,
      uptime: "99.9%",
    },
    {
      id: "security",
      name: "Security Agent",
      type: "Cybersecurity",
      status: "active",
      icon: Shield,
      color: "from-red-500 to-orange-600",
      performance: 95,
      tasks: 892,
      uptime: "99.8%",
    },
    {
      id: "general",
      name: "General Agent",
      type: "General AI",
      status: "active",
      icon: Bot,
      color: "from-blue-500 to-purple-600",
      performance: 97,
      tasks: 2156,
      uptime: "99.9%",
    },
  ])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Agent Control Center</h1>
          <p className="text-gray-300">Monitor and manage your AI agents in real-time</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Total Agents</p>
                  <p className="text-3xl font-bold text-white">3</p>
                </div>
                <Bot className="w-8 h-8 text-purple-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Active Tasks</p>
                  <p className="text-3xl font-bold text-white">4,295</p>
                </div>
                <Activity className="w-8 h-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Avg Performance</p>
                  <p className="text-3xl font-bold text-white">96.7%</p>
                </div>
                <BarChart3 className="w-8 h-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">System Uptime</p>
                  <p className="text-3xl font-bold text-white">99.9%</p>
                </div>
                <Zap className="w-8 h-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Agents Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {activeAgents.map((agent) => (
            <Card
              key={agent.id}
              className="bg-white/10 border-white/20 backdrop-blur-sm hover:bg-white/15 transition-all"
            >
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-12 h-12 bg-gradient-to-r ${agent.color} rounded-lg flex items-center justify-center`}
                    >
                      <agent.icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-white font-semibold">{agent.name}</h3>
                      <p className="text-gray-400 text-sm">{agent.type}</p>
                    </div>
                  </div>
                  <Badge className="bg-green-500/20 text-green-300 border-green-500/30">{agent.status}</Badge>
                </CardTitle>
              </CardHeader>

              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-300">Performance</span>
                    <span className="text-white">{agent.performance}%</span>
                  </div>
                  <Progress value={agent.performance} className="h-2" />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-gray-400 text-xs">Tasks Completed</p>
                    <p className="text-white font-semibold">{agent.tasks.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xs">Uptime</p>
                    <p className="text-white font-semibold">{agent.uptime}</p>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <Button size="sm" className="flex-1 bg-purple-600 hover:bg-purple-700">
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Chat
                  </Button>
                  <Button size="sm" variant="outline" className="border-white/20 text-white hover:bg-white/10">
                    <Settings className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
