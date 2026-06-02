"use client"

import { useRouter, usePathname } from "next/navigation"
import { MessageSquare, Plus, BookOpen, Trash2 } from "lucide-react"
import { useChatStore } from "@/lib/chat-store"
import { cn } from "@/lib/utils"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuAction,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"

export function AppSidebar() {
  const router = useRouter()
  const pathname = usePathname()
  const { chats, currentChatId, createChat, deleteChat, setCurrentChat } = useChatStore()

  const handleNewChat = () => {
    const newChatId = createChat()
    router.push(`/chat/${newChatId}`)
  }

  const handleSelectChat = (chatId: string) => {
    setCurrentChat(chatId)
    router.push(`/chat/${chatId}`)
  }

  const handleDeleteChat = (e: React.MouseEvent, chatId: string) => {
    e.stopPropagation()
    deleteChat(chatId)
    if (currentChatId === chatId) {
      router.push("/")
    }
  }

  const handleKnowledgeBase = () => {
    router.push("/knowledge")
  }

  const formatDate = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) return "Today"
    if (days === 1) return "Yesterday"
    if (days < 7) return `${days} days ago`
    return date.toLocaleDateString()
  }

  return (
    <Sidebar className="border-r border-zinc-800 bg-zinc-950 text-zinc-100">
      <SidebarHeader className="border-b border-zinc-800 p-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
            <MessageSquare className="h-4 w-4 text-white" />
          </div>
          <span className="font-semibold text-zinc-100">AI Chat</span>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton
                onClick={handleNewChat}
                className="bg-white text-zinc-950 hover:bg-zinc-200 hover:text-zinc-950"
              >
                <Plus className="h-4 w-4" />
                <span>New Chat</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>History</SidebarGroupLabel>
          <SidebarGroupContent>
            <ScrollArea className="h-[calc(100vh-320px)]">
              <SidebarMenu>
                {chats.length === 0 ? (
                  <div className="px-2 py-4 text-center text-sm text-zinc-400">
                    No chats yet. Start a new conversation!
                  </div>
                ) : (
                  chats.map((chat) => (
                    <SidebarMenuItem key={chat.id}>
                      <SidebarMenuButton
                        onClick={() => handleSelectChat(chat.id)}
                        isActive={currentChatId === chat.id}
                        className="group px-4 py-8"
                      >
                        <MessageSquare className="h-4 w-4 shrink-0" />
                        <div className="flex flex-col gap-0.5 overflow-hidden">
                          <span className="truncate">{chat.title}</span>
                          <span className="text-xs text-zinc-400">
                            {formatDate(chat.updatedAt)}
                          </span>
                        </div>
                      </SidebarMenuButton>
                      <SidebarMenuAction
                        onClick={(e) => handleDeleteChat(e, chat.id)}
                        showOnHover
                        className="text-zinc-400 hover:text-red-400"
                      >
                        <Trash2 className="h-4 w-4" />
                      </SidebarMenuAction>
                    </SidebarMenuItem>
                  ))
                )}
              </SidebarMenu>
            </ScrollArea>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-zinc-800 p-4">
        <Button
          variant="outline"
          className={cn(
            "w-full justify-start gap-2",
            pathname === "/knowledge" && "bg-white/10 text-zinc-100"
          )}
          onClick={handleKnowledgeBase}
        >
          <BookOpen className="h-4 w-4" />
          Knowledge Base
        </Button>
      </SidebarFooter>
    </Sidebar>
  )
}
