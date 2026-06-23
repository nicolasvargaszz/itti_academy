import { PlusIcon } from "lucide-react"
import type { Session } from "@/types/chat"

interface SidebarProps {
  sessions: Session[]
  activeSessionId: string | null
  onNewChat: () => void
  onSelectSession: (session: Session) => void
}

export function Sidebar({ sessions, activeSessionId, onNewChat, onSelectSession }: SidebarProps) {
  return (
    <aside className="hidden md:flex flex-col w-60 shrink-0 border-r border-[#E4E4E7] bg-[#FAFAF9]">
      {/* Mirror the main header height */}
      <div className="h-14 flex items-center px-4 border-b border-[#E4E4E7]">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-[#00B37E] flex items-center justify-center shrink-0">
            <span className="text-white font-heading font-semibold text-xs leading-none">U</span>
          </div>
          <span className="font-heading font-semibold text-[#18181B] text-sm">Uendi</span>
        </div>
      </div>

      {/* New chat button */}
      <div className="px-3 pt-3 pb-1">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm font-medium text-[#18181B] border border-[#E4E4E7] rounded focus:outline-none focus:ring-2 focus:ring-[#00B37E] focus:ring-offset-1 hover:bg-[#F4F4F5] hover:border-[#00B37E] transition-colors"
        >
          <PlusIcon className="w-3.5 h-3.5 text-[#71717A] shrink-0" />
          Nueva conversación
        </button>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto chat-scroll px-3 pb-4 pt-2">
        {sessions.length === 0 ? (
          <p className="text-xs text-[#71717A] text-center py-6 font-body">
            Sin conversaciones aún
          </p>
        ) : (
          <div className="space-y-0.5">
            <p className="text-xs font-medium text-[#71717A] px-2 pb-1 uppercase tracking-wider font-body">
              Recientes
            </p>
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => onSelectSession(session)}
                className={[
                  "w-full text-left px-2.5 py-2 text-sm rounded truncate transition-colors focus:outline-none focus:ring-2 focus:ring-[#00B37E] focus:ring-offset-1",
                  session.id === activeSessionId
                    ? "bg-[#D1FAF0] text-[#18181B] font-medium"
                    : "text-[#71717A] hover:bg-[#F4F4F5] hover:text-[#18181B]",
                ].join(" ")}
              >
                {session.title}
              </button>
            ))}
          </div>
        )}
      </div>
    </aside>
  )
}
