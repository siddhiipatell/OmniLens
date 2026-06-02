"use client"

import { useState, useRef } from "react"
import { Plus, FileText, Image, Music, Trash2, Upload, X } from "lucide-react"
import { useChatStore, type KnowledgeItem } from "@/lib/chat-store"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export default function KnowledgePage() {
  const { knowledge, addKnowledge, deleteKnowledge, isLoaded } = useChatStore()
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<"text" | "image" | "audio">("text")
  const [title, setTitle] = useState("")
  const [textContent, setTextContent] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [filePreview, setFilePreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setTitle(file.name.split(".")[0])

      // Create preview for images
      if (file.type.startsWith("image/")) {
        const reader = new FileReader()
        reader.onloadend = () => {
          setFilePreview(reader.result as string)
        }
        reader.readAsDataURL(file)
      } else {
        setFilePreview(null)
      }
    }
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    setFilePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleAddKnowledge = async () => {
    if (!title.trim()) return

    if (activeTab === "text") {
      if (!textContent.trim()) return
      addKnowledge({
        type: "text",
        title: title.trim(),
        content: textContent.trim(),
      })
    } else if (selectedFile) {
      const reader = new FileReader()
      reader.onloadend = () => {
        addKnowledge({
          type: activeTab,
          title: title.trim(),
          content: reader.result as string,
          fileName: selectedFile.name,
        })
      }
      reader.readAsDataURL(selectedFile)
    }

    // Reset form
    setTitle("")
    setTextContent("")
    setSelectedFile(null)
    setFilePreview(null)
    setIsDialogOpen(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const getIcon = (type: KnowledgeItem["type"]) => {
    switch (type) {
      case "text":
        return <FileText className="h-5 w-5 text-blue-500" />
      case "image":
        return <Image className="h-5 w-5 text-green-500" />
      case "audio":
        return <Music className="h-5 w-5 text-purple-500" />
    }
  }

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    }).format(date)
  }

  if (!isLoaded) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-zinc-400">Loading...</div>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col bg-zinc-950">
      <div className="border-b border-zinc-800 bg-zinc-950/95 px-6 py-4 backdrop-blur">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-zinc-100">Knowledge Base</h1>
            <p className="text-sm text-zinc-400">
              Add text, images, and audio files to enhance your AI conversations
            </p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Add Knowledge
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Add Knowledge</DialogTitle>
                <DialogDescription>
                  Add content to your knowledge base. This will help the AI provide more relevant responses.
                </DialogDescription>
              </DialogHeader>

              <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)}>
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="text" className="gap-2">
                    <FileText className="h-4 w-4" />
                    Text
                  </TabsTrigger>
                  <TabsTrigger value="image" className="gap-2">
                    <Image className="h-4 w-4" />
                    Image
                  </TabsTrigger>
                  <TabsTrigger value="audio" className="gap-2">
                    <Music className="h-4 w-4" />
                    Audio
                  </TabsTrigger>
                </TabsList>

                <div className="mt-4 space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      placeholder="Enter a title..."
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                    />
                  </div>

                  <TabsContent value="text" className="mt-0 space-y-2">
                    <Label htmlFor="content">Content</Label>
                    <Textarea
                      id="content"
                      placeholder="Enter your text content..."
                      className="min-h-[150px]"
                      value={textContent}
                      onChange={(e) => setTextContent(e.target.value)}
                    />
                  </TabsContent>

                  <TabsContent value="image" className="mt-0 space-y-2">
                    <Label>Upload Image</Label>
                    {selectedFile && filePreview ? (
                      <div className="relative">
                        <img
                          src={filePreview}
                          alt="Preview"
                          className="h-40 w-full rounded-lg border border-zinc-800 object-cover"
                        />
                        <Button
                          variant="destructive"
                          size="icon"
                          className="absolute -right-2 -top-2 h-6 w-6"
                          onClick={handleRemoveFile}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ) : (
                      <div
                        className="flex h-40 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-zinc-700 hover:border-zinc-500"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <Upload className="mb-2 h-8 w-8 text-zinc-400" />
                        <span className="text-sm text-zinc-400">Click to upload an image</span>
                        <span className="text-xs text-zinc-500">PNG, JPG, GIF up to 10MB</span>
                      </div>
                    )}
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={handleFileSelect}
                    />
                  </TabsContent>

                  <TabsContent value="audio" className="mt-0 space-y-2">
                    <Label>Upload Audio</Label>
                    {selectedFile ? (
                      <div className="flex items-center gap-3 rounded-lg border p-3">
                        <Music className="h-8 w-8 text-purple-500" />
                        <div className="flex-1 overflow-hidden">
                          <p className="truncate font-medium">{selectedFile.name}</p>
                          <p className="text-sm text-stone-500">
                            {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={handleRemoveFile}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ) : (
                      <div
                        className="flex h-40 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-zinc-700 hover:border-zinc-500"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <Upload className="mb-2 h-8 w-8 text-zinc-400" />
                        <span className="text-sm text-zinc-400">Click to upload an audio file</span>
                        <span className="text-xs text-zinc-500">MP3, WAV, M4A up to 25MB</span>
                      </div>
                    )}
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="audio/*"
                      className="hidden"
                      onChange={handleFileSelect}
                    />
                  </TabsContent>
                </div>
              </Tabs>

              <DialogFooter>
                <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={handleAddKnowledge}
                  disabled={!title.trim() || (activeTab === "text" ? !textContent.trim() : !selectedFile)}
                >
                  Add Knowledge
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <ScrollArea className="flex-1 p-6">
        {knowledge.length === 0 ? (
          <div className="flex h-[400px] flex-col items-center justify-center text-center">
            <div className="mb-4 rounded-full bg-white/10 p-4">
              <FileText className="h-8 w-8 text-zinc-400" />
            </div>
            <h3 className="mb-1 text-lg font-medium text-zinc-100">No knowledge yet</h3>
            <p className="mb-4 max-w-sm text-sm text-zinc-400">
              Add text, images, or audio files to build your knowledge base and enhance AI responses.
            </p>
            <Button onClick={() => setIsDialogOpen(true)} className="gap-2">
              <Plus className="h-4 w-4" />
              Add Your First Item
            </Button>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {knowledge.map((item) => (
              <Card key={item.id} className="group relative overflow-hidden">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {getIcon(item.type)}
                      <CardTitle className="text-base">{item.title}</CardTitle>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 opacity-0 transition-opacity group-hover:opacity-100"
                      onClick={() => deleteKnowledge(item.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                  <CardDescription>{formatDate(item.createdAt)}</CardDescription>
                </CardHeader>
                <CardContent>
                  {item.type === "text" && (
                    <p className="line-clamp-3 text-sm text-zinc-300">{item.content}</p>
                  )}
                  {item.type === "image" && (
                    <img
                      src={item.content}
                      alt={item.title}
                      className="h-32 w-full rounded-md object-cover"
                    />
                  )}
                  {item.type === "audio" && (
                    <div className="flex items-center gap-2 rounded-md bg-white/5 p-2">
                      <Music className="h-5 w-5 text-purple-500" />
                      <span className="truncate text-sm text-zinc-300">{item.fileName}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  )
}
