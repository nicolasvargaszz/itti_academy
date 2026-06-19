# Frontend — Uendi Chat UI

@../design-system.md

## Stack
- Next.js 14 App Router, TypeScript strict
- Tailwind CSS + shadcn/ui
- Google Fonts: Space Grotesk + Inter + JetBrains Mono

## Responsabilidad
UI del chat de Uendi. Consume la API del backend FastAPI.
**NO llamar a APIs de LLM directamente desde el cliente.**

## Componentes Principales
1. `ChatInterface` — layout principal del chat (sidebar + chat area + input bar)
2. `MessageBubble` — burbuja de mensaje, user o bot, según rol
3. `SourceCitation` — muestra la fuente debajo de mensajes bot
4. `ThinkingIndicator` — tres puntos animados mientras el backend procesa
5. `AdminPanel` — tabla para ver documentos indexados

## Variables de Entorno
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Calls
- Chat: `POST /api/v1/chat` → `{ query: string, history: Message[] }`
- Admin docs: `GET /api/v1/admin/documents`
- Health: `GET /health`

## Reglas
- NUNCA hardcodear URLs — siempre `process.env.NEXT_PUBLIC_API_URL`
- SIEMPRE aplicar todos los tokens del design-system.md
- Verificar el checklist de estados de componentes antes de entregar
- Mobile-first: el chat debe funcionar bien en 375px de ancho