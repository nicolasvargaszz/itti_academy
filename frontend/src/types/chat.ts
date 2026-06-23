export interface Source {
  title: string
  url?: string
  doc_id?: string
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: Source[]
  timestamp: Date
}

export interface Session {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
}

export interface ChatRequest {
  query: string
  history: { role: string; content: string }[]
}

export interface ChatResponse {
  answer: string
  sources: Source[]
}
