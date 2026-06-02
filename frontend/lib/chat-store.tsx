"use client"

import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from "react"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  createdAt: Date
  imageData?: string
}

export interface Chat {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}

export interface KnowledgeItem {
  id: string
  type: "text" | "image" | "audio"
  title: string
  content: string // For text, this is the content. For files, this is the base64 data
  fileName?: string
  createdAt: Date
}

interface ChatStoreContextType {
  chats: Chat[]
  currentChatId: string | null
  knowledge: KnowledgeItem[]
  createChat: () => string
  deleteChat: (id: string) => void
  setCurrentChat: (id: string | null) => void
  getCurrentChat: () => Chat | null
  updateChatMessages: (chatId: string, messages: Message[]) => void
  addKnowledge: (item: Omit<KnowledgeItem, "id" | "createdAt">) => void
  deleteKnowledge: (id: string) => void
  isLoaded: boolean
}

const ChatStoreContext = createContext<ChatStoreContextType | null>(null)

const CHATS_STORAGE_KEY = "chat-store-chats"
const CURRENT_CHAT_KEY = "chat-store-current"
const KNOWLEDGE_STORAGE_KEY = "chat-store-knowledge"

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
}

function generateChatTitle(messages: Message[]): string {
  const firstUserMessage = messages.find((m) => m.role === "user")
  if (firstUserMessage) {
    const content = firstUserMessage.content.trim()
    if (content.length > 30) {
      return content.substring(0, 30) + "..."
    }
    return content || "New Chat"
  }
  return "New Chat"
}

export function ChatStoreProvider({ children }: { children: ReactNode }) {
  const [chats, setChats] = useState<Chat[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [knowledge, setKnowledge] = useState<KnowledgeItem[]>([])
  const [isLoaded, setIsLoaded] = useState(false)

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const storedChats = localStorage.getItem(CHATS_STORAGE_KEY)
      if (storedChats) {
        const parsed = JSON.parse(storedChats)
        const chatsWithDates = parsed.map((chat: Chat) => ({
          ...chat,
          createdAt: new Date(chat.createdAt),
          updatedAt: new Date(chat.updatedAt),
          messages: chat.messages.map((msg: Message) => ({
            ...msg,
            createdAt: new Date(msg.createdAt),
          })),
        }))
        setChats(chatsWithDates)
      }

      const storedCurrentId = localStorage.getItem(CURRENT_CHAT_KEY)
      if (storedCurrentId) {
        setCurrentChatId(storedCurrentId)
      }

      const storedKnowledge = localStorage.getItem(KNOWLEDGE_STORAGE_KEY)
      if (storedKnowledge) {
        const parsed = JSON.parse(storedKnowledge)
        const knowledgeWithDates = parsed.map((item: KnowledgeItem) => ({
          ...item,
          createdAt: new Date(item.createdAt),
        }))
        setKnowledge(knowledgeWithDates)
      }
    } catch (e) {
      console.error("Failed to load chat store from localStorage:", e)
    } finally {
      setIsLoaded(true)
    }
  }, [])

  // Persist chats to localStorage
  useEffect(() => {
    if (!isLoaded) return
    try {
      localStorage.setItem(CHATS_STORAGE_KEY, JSON.stringify(chats))
    } catch (e) {
      console.error("Failed to save chats to localStorage:", e)
    }
  }, [chats, isLoaded])

  // Persist current chat ID
  useEffect(() => {
    if (!isLoaded) return
    try {
      if (currentChatId) {
        localStorage.setItem(CURRENT_CHAT_KEY, currentChatId)
      } else {
        localStorage.removeItem(CURRENT_CHAT_KEY)
      }
    } catch (e) {
      console.error("Failed to save current chat ID to localStorage:", e)
    }
  }, [currentChatId, isLoaded])

  // Persist knowledge to localStorage
  useEffect(() => {
    if (!isLoaded) return
    try {
      localStorage.setItem(KNOWLEDGE_STORAGE_KEY, JSON.stringify(knowledge))
    } catch (e) {
      console.error("Failed to save knowledge to localStorage:", e)
    }
  }, [knowledge, isLoaded])

  const createChat = useCallback(() => {
    const newChat: Chat = {
      id: generateId(),
      title: "New Chat",
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    setChats((prev) => [newChat, ...prev])
    setCurrentChatId(newChat.id)
    return newChat.id
  }, [])

  const deleteChat = useCallback(
    (id: string) => {
      setChats((prev) => prev.filter((chat) => chat.id !== id))
      if (currentChatId === id) {
        setCurrentChatId(null)
      }
    },
    [currentChatId]
  )

  const setCurrentChat = useCallback((id: string | null) => {
    setCurrentChatId(id)
  }, [])

  const getCurrentChat = useCallback(() => {
    if (!currentChatId) return null
    return chats.find((chat) => chat.id === currentChatId) || null
  }, [chats, currentChatId])

  const updateChatMessages = useCallback((chatId: string, messages: Message[]) => {
    setChats((prev) =>
      prev.map((chat) => {
        if (chat.id === chatId) {
          return {
            ...chat,
            messages,
            title: generateChatTitle(messages),
            updatedAt: new Date(),
          }
        }
        return chat
      })
    )
  }, [])

  const addKnowledge = useCallback((item: Omit<KnowledgeItem, "id" | "createdAt">) => {
    const newItem: KnowledgeItem = {
      ...item,
      id: generateId(),
      createdAt: new Date(),
    }
    setKnowledge((prev) => [newItem, ...prev])
  }, [])

  const deleteKnowledge = useCallback((id: string) => {
    setKnowledge((prev) => prev.filter((item) => item.id !== id))
  }, [])

  return (
    <ChatStoreContext.Provider
      value={{
        chats,
        currentChatId,
        knowledge,
        createChat,
        deleteChat,
        setCurrentChat,
        getCurrentChat,
        updateChatMessages,
        addKnowledge,
        deleteKnowledge,
        isLoaded,
      }}
    >
      {children}
    </ChatStoreContext.Provider>
  )
}

export function useChatStore() {
  const context = useContext(ChatStoreContext)
  if (!context) {
    throw new Error("useChatStore must be used within a ChatStoreProvider")
  }
  return context
}
