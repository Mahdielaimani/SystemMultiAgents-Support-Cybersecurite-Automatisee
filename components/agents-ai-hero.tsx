"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Bot, Shield, MessageSquare, Sparkles, ArrowRight, Play, ChevronDown, Menu, X } from "lucide-react"

export function AgentsAiHero() {
  const [email, setEmail] = useState("")
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Background Matrix Effect */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `url('/images/code-matrix-bg.png')`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      />

      {/* Floating Code Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {Array.from({ length: 50 }).map((_, i) => (
          <div
            key={i}
            className="absolute text-purple-500/30 font-mono text-xs animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 10}s`,
              animationDuration: `${15 + Math.random() * 10}s`,
            }}
          >
            {["01", "10", "11", "00", "AI", "ML", "NN", "DL"][Math.floor(Math.random() * 8)]}
          </div>
        ))}
      </div>

      {/* Navigation */}
      <nav className="relative z-50 flex items-center justify-between p-6 lg:px-12">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <span className="text-white font-bold text-xl">NextGen</span>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden lg:flex items-center space-x-8">
          <button className="text-white hover:text-purple-400 transition-colors flex items-center space-x-1">
            <span>Agents</span>
            <ChevronDown className="w-4 h-4" />
          </button>
          <button className="text-white hover:text-purple-400 transition-colors">Case Studies</button>
          <button className="text-white hover:text-purple-400 transition-colors">Marketplace</button>
          <Button variant="outline" className="border-purple-500 text-purple-400 hover:bg-purple-500 hover:text-white">
            Sign In
          </Button>
        </div>

        {/* Mobile Menu Button */}
        <button className="lg:hidden text-white" onClick={() => setIsMenuOpen(!isMenuOpen)}>
          {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </nav>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="lg:hidden absolute top-20 left-0 right-0 bg-black/95 backdrop-blur-sm z-40 p-6">
          <div className="space-y-4">
            <button className="block text-white hover:text-purple-400 transition-colors">Agents</button>
            <button className="block text-white hover:text-purple-400 transition-colors">Case Studies</button>
            <button className="block text-white hover:text-purple-400 transition-colors">Marketplace</button>
            <Button
              variant="outline"
              className="w-full border-purple-500 text-purple-400 hover:bg-purple-500 hover:text-white"
            >
              Sign In
            </Button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-[80vh] px-6 lg:px-12">
        {/* Central AI Agent Figure */}
        <div className="relative mb-12">
          {/* Glow Effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/30 to-pink-500/30 rounded-full blur-3xl scale-150"></div>

          {/* Agent Silhouette */}
          <div className="relative w-64 h-64 lg:w-80 lg:h-80">
            <img
              src="/images/ai-agent-silhouette.png"
              alt="AI Agent"
              className="w-full h-full object-contain filter brightness-0 invert opacity-80"
            />
            {/* Animated Ring */}
            <div className="absolute inset-0 border-2 border-purple-500/50 rounded-full animate-pulse"></div>
            <div className="absolute inset-4 border border-pink-500/30 rounded-full animate-spin-slow"></div>
          </div>
        </div>

        {/* Hero Text */}
        <div className="text-center max-w-4xl mx-auto mb-12">
          <h1 className="text-4xl lg:text-6xl font-bold text-white mb-6 leading-tight">
            Automate Your Business with{" "}
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              NextGen.ai
            </span>
          </h1>

          <p className="text-gray-300 text-lg lg:text-xl mb-8 leading-relaxed">
            Discover how our innovative AI agents can automate your full-time operations and earn lifetime recurring
            revenue for referring. Join us in transforming the way you work with cutting-edge automation.
          </p>

          {/* Agent Types */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            <Badge className="bg-purple-500/20 text-purple-300 border-purple-500/30 px-4 py-2">
              <MessageSquare className="w-4 h-4 mr-2" />
              Support Agent
            </Badge>
            <Badge className="bg-pink-500/20 text-pink-300 border-pink-500/30 px-4 py-2">
              <Shield className="w-4 h-4 mr-2" />
              Security Agent
            </Badge>
            <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30 px-4 py-2">
              <Sparkles className="w-4 h-4 mr-2" />
              General Agent
            </Badge>
          </div>

          {/* Email Signup */}
          <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto mb-8">
            <Input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-white/10 border-white/20 text-white placeholder:text-gray-400 focus:border-purple-500"
            />
            <Button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-8">
              Get Started
            </Button>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-8"
            >
              <Play className="w-5 h-5 mr-2" />
              Try Demo
            </Button>
            <Button size="lg" variant="outline" className="border-white/20 text-white hover:bg-white/10">
              Learn More
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto">
          <div className="text-center">
            <div className="text-3xl font-bold text-white mb-2">10K+</div>
            <div className="text-gray-400">Active Agents</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white mb-2">99.9%</div>
            <div className="text-gray-400">Uptime</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white mb-2">24/7</div>
            <div className="text-gray-400">Support</div>
          </div>
        </div>
      </div>

      {/* Bottom Gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-purple-900/20 to-transparent"></div>
    </div>
  )
}
