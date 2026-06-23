"use client"

import React from "react"
import { cx } from "class-variance-authority"
import { AnimatePresence, motion } from "motion/react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

// ─── ColorOrb ────────────────────────────────────────────────────────────────
// Inline CSS vars feed the `.color-orb` pseudo-elements defined in globals.css.
// No styled-jsx needed — the global class handles all pseudo-element rules.

interface OrbProps {
  dimension?: string
  className?: string
  tones?: {
    base?: string
    accent1?: string
    accent2?: string
    accent3?: string
  }
  spinDuration?: number
}

const ColorOrb: React.FC<OrbProps> = ({
  dimension = "192px",
  className,
  tones,
  spinDuration = 20,
}) => {
  const fallback = {
    base: "oklch(95% 0.02 162)",
    accent1: "oklch(72% 0.2 162)",
    accent2: "oklch(78% 0.15 160)",
    accent3: "oklch(68% 0.18 158)",
  }
  const palette = { ...fallback, ...tones }
  const dim = parseInt(dimension.replace("px", ""), 10)
  const blur = dim < 50 ? Math.max(dim * 0.008, 1) : Math.max(dim * 0.015, 4)
  const contrast = dim < 50 ? Math.max(dim * 0.004, 1.2) : Math.max(dim * 0.008, 1.5)
  const dot = dim < 50 ? Math.max(dim * 0.004, 0.05) : Math.max(dim * 0.008, 0.1)
  const shadow = dim < 50 ? Math.max(dim * 0.004, 0.5) : Math.max(dim * 0.008, 2)
  const adjContrast = dim < 30 ? 1.1 : dim < 50 ? Math.max(contrast * 1.2, 1.3) : contrast

  return (
    <div
      className={cn("color-orb", className)}
      style={
        {
          width: dimension,
          height: dimension,
          "--base": palette.base,
          "--accent1": palette.accent1,
          "--accent2": palette.accent2,
          "--accent3": palette.accent3,
          "--spin-duration": `${spinDuration}s`,
          "--blur": `${blur}px`,
          "--contrast": adjContrast,
          "--dot": `${dot}px`,
          "--shadow": `${shadow}px`,
        } as React.CSSProperties
      }
    />
  )
}

// ─── Uendo green orb tones (used in both dock bar and expanded form) ──────────
const UENDI_ORB_TONES = {
  base: "oklch(22.64% 0 0)",
  accent1: "oklch(72% 0.2 162)",
  accent2: "oklch(78% 0.15 160)",
  accent3: "oklch(68% 0.18 158)",
}

// ─── Context ──────────────────────────────────────────────────────────────────
const SPEED = 1
const FORM_HEIGHT = 180

interface Ctx {
  showForm: boolean
  triggerOpen: () => void
  triggerClose: () => void
  disabled: boolean
}

const FormCtx = React.createContext({} as Ctx)
const useFormCtx = () => React.useContext(FormCtx)

// ─── MorphPanel ───────────────────────────────────────────────────────────────

interface MorphPanelProps {
  onSubmit: (message: string) => void
  disabled?: boolean
}

export function MorphPanel({ onSubmit, disabled = false }: MorphPanelProps) {
  const wrapperRef = React.useRef<HTMLDivElement>(null)
  const textareaRef = React.useRef<HTMLTextAreaElement | null>(null)
  const [showForm, setShowForm] = React.useState(false)

  const triggerClose = React.useCallback(() => {
    setShowForm(false)
    textareaRef.current?.blur()
  }, [])

  const triggerOpen = React.useCallback(() => {
    if (disabled) return
    setShowForm(true)
    setTimeout(() => textareaRef.current?.focus())
  }, [disabled])

  const handleSuccess = React.useCallback(
    (message: string) => {
      onSubmit(message)
      triggerClose()
    },
    [onSubmit, triggerClose],
  )

  React.useEffect(() => {
    function handler(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node) && showForm) {
        triggerClose()
      }
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [showForm, triggerClose])

  const ctx = React.useMemo(
    () => ({ showForm, triggerOpen, triggerClose, disabled }),
    [showForm, triggerOpen, triggerClose, disabled],
  )

  return (
    <div className="flex items-center justify-center w-full py-3 px-4">
      <motion.div
        ref={wrapperRef}
        className={cx("bg-white relative z-10 flex flex-col items-center overflow-hidden border border-[#E4E4E7]")}
        initial={false}
        animate={{
          width: showForm ? "100%" : "auto",
          height: showForm ? FORM_HEIGHT : 44,
          borderRadius: showForm ? 12 : 22,
        }}
        transition={{
          type: "spring",
          stiffness: 550 / SPEED,
          damping: 45,
          mass: 0.7,
          delay: showForm ? 0 : 0.08,
        }}
        style={{ maxWidth: 640 }}
      >
        <FormCtx.Provider value={ctx}>
          <DockBar />
          <InputForm ref={textareaRef} onSuccess={handleSuccess} />
        </FormCtx.Provider>
      </motion.div>
    </div>
  )
}

// ─── DockBar (collapsed state) ────────────────────────────────────────────────

function DockBar() {
  const { showForm, triggerOpen, disabled } = useFormCtx()
  return (
    <footer className="mt-auto flex h-[44px] items-center justify-center whitespace-nowrap select-none">
      <div className="flex items-center gap-2 px-3">
        <AnimatePresence mode="wait">
          {showForm ? (
            <motion.div
              key="blank"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0 }}
              exit={{ opacity: 0 }}
              className="h-5 w-5"
            />
          ) : (
            <motion.div
              key="orb"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <ColorOrb dimension="20px" tones={UENDI_ORB_TONES} />
            </motion.div>
          )}
        </AnimatePresence>

        <Button
          type="button"
          variant="ghost"
          onClick={triggerOpen}
          disabled={disabled}
          className="h-fit rounded-full px-2 py-0.5 text-sm text-[#71717A] hover:text-[#18181B]"
        >
          {disabled ? "Uendi está respondiendo…" : "Hacé tu consulta"}
        </Button>
      </div>
    </footer>
  )
}

// ─── InputForm (expanded state) ───────────────────────────────────────────────

const InputForm = React.forwardRef<HTMLTextAreaElement, { onSuccess: (msg: string) => void }>(
  function InputForm({ onSuccess }, ref) {
    const { triggerClose, showForm, disabled } = useFormCtx()
    const btnRef = React.useRef<HTMLButtonElement>(null)

    function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
      e.preventDefault()
      const form = e.currentTarget
      const data = new FormData(form)
      const message = ((data.get("message") as string) ?? "").trim()
      if (!message) return
      onSuccess(message)
      form.reset()
    }

    function handleKeys(e: React.KeyboardEvent<HTMLTextAreaElement>) {
      if (e.key === "Escape") triggerClose()
      if (e.key === "Enter" && e.metaKey) {
        e.preventDefault()
        btnRef.current?.click()
      }
    }

    return (
      <form
        onSubmit={handleSubmit}
        className="absolute bottom-0 left-0 right-0"
        style={{ height: FORM_HEIGHT, pointerEvents: showForm ? "all" : "none" }}
      >
        <AnimatePresence>
          {showForm && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ type: "spring", stiffness: 550 / SPEED, damping: 45, mass: 0.7 }}
              className="flex h-full flex-col p-1"
            >
              <div className="flex items-center justify-between py-1 px-1">
                <p className="ml-9 text-sm font-medium text-[#18181B] select-none">Uendi</p>
                <button
                  type="submit"
                  ref={btnRef}
                  disabled={disabled}
                  className="flex items-center gap-1 pr-1 text-[#71717A] hover:text-[#18181B] disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
                >
                  <KeyHint>⌘</KeyHint>
                  <KeyHint className="w-fit">Enter</KeyHint>
                </button>
              </div>
              <textarea
                ref={ref}
                placeholder="Preguntale a Uendi…"
                name="message"
                disabled={disabled}
                className="h-full w-full resize-none rounded-md p-4 pt-2 text-sm text-[#18181B] placeholder:text-[#71717A] bg-transparent outline-none disabled:opacity-40"
                required
                onKeyDown={handleKeys}
                spellCheck={false}
              />
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {showForm && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="absolute top-2.5 left-3 pointer-events-none"
            >
              <ColorOrb dimension="20px" tones={UENDI_ORB_TONES} />
            </motion.div>
          )}
        </AnimatePresence>
      </form>
    )
  },
)

function KeyHint({ children, className }: { children: string; className?: string }) {
  return (
    <kbd
      className={cx(
        "flex h-5 w-5 items-center justify-center rounded border border-[#E4E4E7] px-1 text-xs font-sans text-[#71717A]",
        className,
      )}
    >
      {children}
    </kbd>
  )
}

export default MorphPanel
