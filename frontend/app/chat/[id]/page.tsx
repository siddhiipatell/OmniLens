import { ChatShell } from "@/components/chat/chat-shell"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Chat - AI Assistant",
  description: "Chat with our AI assistant powered by Gemini",
}

export default async function ChatPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return <ChatShell chatId={id} />
}
