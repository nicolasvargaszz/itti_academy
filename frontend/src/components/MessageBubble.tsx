import { SourceCitation } from "./SourceCitation"
import type { Message } from "@/types/chat"

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user"

  return (
    <div className={["flex flex-col gap-1.5", isUser ? "items-end" : "items-start"].join(" ")}>
      <div
        className={[
          "px-4 py-3 text-sm leading-relaxed font-body",
          isUser
            ? "bg-[#18181B] text-white rounded-xl rounded-br-sm max-w-[75%]"
            : "bg-[#F4F4F5] text-[#18181B] rounded-xl rounded-bl-sm max-w-[80%]",
        ].join(" ")}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <BotContent content={message.content} />
        )}
      </div>

      {!isUser && message.sources && message.sources.length > 0 && (
        <div className="max-w-[80%] w-full space-y-1">
          {message.sources.map((source, i) => (
            <SourceCitation key={i} source={source} />
          ))}
        </div>
      )}
    </div>
  )
}

// Renders bot text: paragraph splits, ordered/unordered lists, **bold**.
function BotContent({ content }: { content: string }) {
  const blocks = content.split(/\n{2,}/).filter(Boolean)

  return (
    <div className="space-y-2">
      {blocks.map((block, i) => {
        const lines = block.split("\n")

        if (/^\d+\.\s/.test(lines[0].trim())) {
          return (
            <ol key={i} className="list-decimal list-inside space-y-1 pl-1">
              {lines.map((line, j) => (
                <li key={j}>{renderInline(line.replace(/^\d+\.\s/, "").trim())}</li>
              ))}
            </ol>
          )
        }

        if (/^[-•]\s/.test(lines[0].trim())) {
          return (
            <ul key={i} className="list-disc list-inside space-y-1 pl-1">
              {lines.map((line, j) => (
                <li key={j}>{renderInline(line.replace(/^[-•]\s/, "").trim())}</li>
              ))}
            </ul>
          )
        }

        return (
          <p key={i} className="leading-relaxed">
            {renderInline(lines.join(" "))}
          </p>
        )
      })}
    </div>
  )
}

function renderInline(text: string) {
  return text.split(/(\*\*[^*]+\*\*)/).map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={i} className="font-semibold">
        {part.slice(2, -2)}
      </strong>
    ) : (
      <span key={i}>{part}</span>
    ),
  )
}
