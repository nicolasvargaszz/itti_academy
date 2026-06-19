# Design System — Uendi Chat (Anti-AI-Slop)

## Regla de Oro
Antes de generar CUALQUIER componente visual, verificar este archivo.
NO defaultear a: Inter sin elegir, azules/violetas, gradientes, glassmorphism, layouts Stripe-lookalike.

## Tipografía
| Rol | Fuente | Tamaño | Peso |
|-----|--------|--------|------|
| Headings | Space Grotesk | 32/24/20/18px | 600 |
| Body | Inter (elegido explícitamente) | 16px | 400 |
| Labels | Inter | 13px | 500 |
| Código/logs | JetBrains Mono | 13px | 400 |

```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=Inter:wght@400;500&family=JetBrains+Mono&display=swap" rel="stylesheet">
```

## Tokens de Color

```css
:root {
  --color-bg:              #FAFAF9;
  --color-surface:         #FFFFFF;
  --color-surface-alt:     #F4F4F0;

  --color-primary:         #F97316;
  --color-primary-dark:    #EA6C0A;
  --color-primary-muted:   #FED7AA;

  --color-text:            #18181B;
  --color-text-muted:      #71717A;
  --color-text-inverse:    #FAFAF9;

  --color-border:          #E4E4E7;
  --color-border-focus:    #F97316;

  --color-success:         #16A34A;
  --color-error:           #DC2626;

  --color-user-bubble:     #18181B;
  --color-bot-bubble:      #F4F4F0;
  --color-citation-bg:     #FFF7ED;
  --color-citation-border: #FDBA74;
}
```

**PROHIBIDO:** #3B82F6 (azul), #6366F1 (indigo), #8B5CF6 (violeta), cualquier gradiente, backdrop-filter blur.

## Espaciado y Forma
- Base: 4px. Escala: 4/8/12/16/24/32/48/64px
- Botones/inputs: border-radius 4px
- Chat bubbles: border-radius 12px
- Cards: border-radius 8px
- Sombras: solo 3 niveles (sm/md/lg). Sin glows ni sombras de color.

## Componentes

### Botón primario
```
bg-[--color-primary] text-white rounded px-4 py-2 text-sm font-medium
hover: bg-[--color-primary-dark]
disabled: opacity-40 cursor-not-allowed
loading: spinner inside, mismo width
```

### Input
```
border border-[--color-border] rounded bg-white px-3 py-2 text-sm
focus: ring-2 ring-[--color-border-focus] border-transparent
error: border-[--color-error] ring-2 ring-red-100
```

### Chat bubbles
```
User:  self-end bg-[--color-user-bubble] text-[--color-text-inverse]
       rounded-xl rounded-br-sm max-w-[75%] px-4 py-3 text-sm

Bot:   self-start bg-[--color-bot-bubble] text-[--color-text]
       rounded-xl rounded-bl-sm max-w-[80%] px-4 py-3 text-sm

Citation: border-l-2 border-[--color-citation-border] bg-[--color-citation-bg]
          px-3 py-2 text-xs text-[--color-text-muted]
```

## Layout del Chat
```
┌─────────────────────────────────────────────┐
│  HEADER: logo · "Uendi — Asistente Banco Ueno"│
├──────────┬──────────────────────────────────┤
│ SIDEBAR  │  ÁREA DE CHAT                    │
│ (240px)  │                                  │
│          │  [bot bubble]                    │
│ Historial│        [user bubble]             │
│          │  [bot bubble]                    │
│          │  └─ [citation]                   │
│          ├──────────────────────────────────┤
│          │  [input]              [Enviar →] │
└──────────┴──────────────────────────────────┘
```

## Qué NUNCA generar para Uendi
- Hero sections con gradiente
- Icon grids de 3 columnas
- Glassmorphism (backdrop-blur + transparencia)
- FAB buttons con sombra de color
- Cards con header de gradiente
- Purple/violet/blue como accent
- Avatares animados para el bot (usar texto o icono simple)

## Checklist antes de entregar cualquier componente
- [ ] Estado default
- [ ] Estado hover
- [ ] Estado focus (ring visible)
- [ ] Estado loading
- [ ] Estado vacío (empty state)
- [ ] Estado error
- [ ] Estado disabled

## Tailwind Config
```js
theme: {
  extend: {
    colors: {
      primary: { DEFAULT: '#F97316', dark: '#EA6C0A', muted: '#FED7AA' },
      surface: { DEFAULT: '#FFFFFF', alt: '#F4F4F0' },
      utext: { DEFAULT: '#18181B', muted: '#71717A', inverse: '#FAFAF9' },
      uborder: { DEFAULT: '#E4E4E7', focus: '#F97316' },
      citation: { bg: '#FFF7ED', border: '#FDBA74' },
    },
    fontFamily: {
      heading: ['Space Grotesk', 'sans-serif'],
      body: ['Inter', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
  },
}
```