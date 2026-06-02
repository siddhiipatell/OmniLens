"use client"

import { AnimatedOrb } from "./animated-orb"

export function TypingIndicator() {
  return (
    <div className="flex gap-3 max-w-[90%] md:max-w-[80%] mr-auto animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div className="shrink-0">
        <AnimatedOrb size={32} />
      </div>

      {/* Typing dots */}
      <div
        className="rounded-2xl rounded-bl-md border border-zinc-800 bg-zinc-900 px-4 py-3"
        style={{
          boxShadow:
            "rgba(0, 0, 0, 0.3) 0px 0px 0px 1px, rgba(0, 0, 0, 0.18) 0px 1px 1px -0.5px, rgba(0, 0, 0, 0.16) 0px 3px 3px -1.5px, rgba(0, 0, 0, 0.14) 0px 6px 6px -3px, rgba(0, 0, 0, 0.12) 0px 12px 12px -6px, rgba(0, 0, 0, 0.1) 0px 24px 24px -12px",
        }}
        role="status"
        aria-label="Assistant is typing"
      >
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "0ms" }} />
          <span className="w-2 h-2 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "150ms" }} />
          <span className="w-2 h-2 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  )
}
