import type { Source } from "@/types/chat"

export function SourceCitation({ source }: { source: Source }) {
  return (
    <div className="border-l-2 border-[#6EE7CA] bg-[#F0FDF9] px-3 py-2 rounded-r-md">
      <p className="text-xs text-[#71717A] font-body leading-relaxed">
        <span className="font-medium text-[#18181B]">Fuente: </span>
        {source.url ? (
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#00B37E] hover:underline underline-offset-2 transition-colors"
          >
            {source.title}
          </a>
        ) : (
          <span>{source.title}</span>
        )}
      </p>
    </div>
  )
}
