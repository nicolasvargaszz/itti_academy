"use client"

import React from "react"
import { Sidebar } from "./Sidebar"
import { MessageBubble } from "./MessageBubble"
import { ThinkingIndicator } from "./ThinkingIndicator"
import { MorphPanel } from "./ui/ai-input"
import type { Message, Session } from "@/types/chat"

const SUGGESTIONS = [
  "¿Cómo abro una cuenta en Ueno?",
  "¿Qué es un CDA y cómo funciona?",
  "¿Cómo invierto en fondos mutuos?",
]

export function ChatInterface() {
  const [sessions, setSessions] = React.useState<Session[]>([])
  const [activeSessionId, setActiveSessionId] = React.useState<string | null>(null)
  const [messages, setMessages] = React.useState<Message[]>([])
  const [isLoading, setIsLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const scrollRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isLoading])

  const handleSubmit = React.useCallback(
    async (query: string) => {
      if (!query.trim() || isLoading) return
      setError(null)

      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: query,
        timestamp: new Date(),
      }
      const nextMessages = [...messages, userMsg]
      setMessages(nextMessages)
      setIsLoading(true)

      if (!activeSessionId) {
        const newSession: Session = {
          id: crypto.randomUUID(),
          title: query.slice(0, 42),
          messages: nextMessages,
          createdAt: new Date(),
        }
        setSessions((prev) => [newSession, ...prev])
        setActiveSessionId(newSession.id)
      }

      try {
        const history = messages.map((m) => ({ role: m.role, content: m.content }))
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query, history }),
        })

        if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`)

        const data = await res.json()
        const botMsg: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.answer,
          sources: data.sources ?? [],
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, botMsg])
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "No se pudo conectar con el servidor. Verificá tu conexión e intentá de nuevo.",
        )
      } finally {
        setIsLoading(false)
      }
    },
    [messages, isLoading, activeSessionId],
  )

  const handleNewChat = React.useCallback(() => {
    setMessages([])
    setActiveSessionId(null)
    setError(null)
  }, [])

  const handleSelectSession = React.useCallback((session: Session) => {
    setMessages(session.messages)
    setActiveSessionId(session.id)
    setError(null)
  }, [])

  return (
    <div className="flex h-screen bg-[#FAFAF9]">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
      />

      <main className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="h-14 flex items-center px-6 border-b border-[#E4E4E7] bg-white shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded bg-[#00B37E] flex items-center justify-center shrink-0">
              <span className="text-white font-heading font-semibold text-sm leading-none">U</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="font-heading font-semibold text-[#18181B] text-sm leading-tight">
                Uendi
              </span>
              <span className="text-[#71717A] text-xs font-body">Asistente Banco Ueno</span>
            </div>
          </div>
        </header>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto chat-scroll">
          {messages.length === 0 ? (
            <WelcomeState onSuggest={handleSubmit} isLoading={isLoading} />
          ) : (
            <div className="max-w-2xl mx-auto px-4 py-6 space-y-3">
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {isLoading && <ThinkingIndicator />}
              {error && (
                <div className="flex items-start justify-between gap-4 text-sm text-[#DC2626] bg-red-50 border border-red-100 rounded-lg px-4 py-3">
                  <span className="font-body leading-relaxed">{error}</span>
                  <button
                    onClick={() => setError(null)}
                    className="shrink-0 text-xs text-[#71717A] hover:text-[#18181B] transition-colors underline underline-offset-2 mt-0.5"
                  >
                    Cerrar
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="shrink-0 border-t border-[#E4E4E7] bg-white">
          <MorphPanel onSubmit={handleSubmit} disabled={isLoading} />
        </div>
      </main>
    </div>
  )
}

// ─── Welcome / empty state ─────────────────────────────────────────────────────

function WelcomeState({
  onSuggest,
  isLoading,
}: {
  onSuggest: (q: string) => void
  isLoading: boolean
}) {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[360px] text-center px-4">
      <div className="mb-8">
        <div className="w-14 h-14 rounded-xl bg-[#00B37E] flex items-center justify-center mx-auto mb-5">
          <span className="text-white font-heading font-semibold text-2xl leading-none">U</span>
        </div>
        <h1 className="font-heading font-semibold text-[#18181B] text-xl tracking-tight">
          Bienvenido a Uendi
        </h1>
        <p className="text-[#71717A] text-sm mt-1.5 max-w-xs mx-auto font-body leading-relaxed">
          Asistente del Banco Ueno. Hacé tus preguntas sobre productos bancarios, cuentas e inversiones.
        </p>
      </div>

      <div className="flex flex-col gap-2 w-full max-w-sm">
        {SUGGESTIONS.map((q) => (
          <button
            key={q}
            disabled={isLoading}
            onClick={() => onSuggest(q)}
            className="text-left px-4 py-3 text-sm text-[#18181B] font-body border border-[#E4E4E7] rounded-lg hover:border-[#00B37E] hover:bg-[#F0FDF9] focus:outline-none focus:ring-2 focus:ring-[#00B37E] focus:ring-offset-1 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  )
}
