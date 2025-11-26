import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent } from "@/components/ui/card";
import { Send, Bot, User, Loader2, FileText, X, Upload } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { documentApi, queryApi } from "@/lib/api";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { DocumentUpload } from "@/components/DocumentUpload";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
  sources?: Array<{
    text: string;
    score: number;
  }>;
}

interface Document {
  id: number;
  originalName: string;
  uploadDate: string;
  previewText: string;
}

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your AI learning assistant. I can help you answer questions, create study plans, or answer questions based on your uploaded documents. How can I help you?",
      role: "assistant",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [isDocumentMode, setIsDocumentMode] = useState(false);
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Get all documents
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const docs = await documentApi.getAllDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user",
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Call Gemini API in both document mode and general chat mode
      const response = await queryApi.sendQuery(
        isDocumentMode && selectedDocument ? selectedDocument : null, 
        input
      );
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.answer,
        role: "assistant",
        timestamp: new Date(),
        sources: response.sources,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Query failed:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, an error occurred while processing your question. Please try again later.',
        role: "assistant",
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleUploadSuccess = async (document: any) => {
    setIsUploadDialogOpen(false);
    await fetchDocuments();
    setSelectedDocument(document.id.toString());
    setIsDocumentMode(true);
    
    // Add system message to notify user of successful upload
    const systemMessage: Message = {
      id: Date.now().toString(),
      content: `Document "${document.originalName}" has been successfully uploaded. You can now ask questions about this document.`,
      role: "assistant",
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, systemMessage]);
  };

  const handleDeleteDocument = async (id: string) => {
    try {
      await documentApi.deleteDocument(id);
      await fetchDocuments();
      
      if (selectedDocument === id) {
        setSelectedDocument(null);
        setIsDocumentMode(false);
      }
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-card border-b border-border sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold text-education-blue">
                AI Learning Assistant
              </h1>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Bot className="h-4 w-4" />
                <span>Smart Chat</span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Document
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Upload Document</DialogTitle>
                  </DialogHeader>
                  <DocumentUpload onUploadSuccess={handleUploadSuccess} />
                </DialogContent>
              </Dialog>
              
              <Button 
                variant="outline" 
                onClick={() => window.history.back()}
                size="sm"
              >
                Back
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 h-[calc(100vh-4rem)] flex flex-col">
        <Card className="flex-1 flex flex-col">
          <CardContent className="flex-1 flex flex-col p-0">
            <ScrollArea 
              ref={scrollAreaRef}
              className="flex-1 p-6"
            >
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {message.role === "assistant" && (
                      <div className="flex-shrink-0 w-8 h-8 bg-education-blue rounded-full flex items-center justify-center">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                    )}
                    <div
                      className={`max-w-[70%] rounded-lg px-4 py-3 ${
                        message.role === "user"
                          ? "bg-education-blue text-white"
                          : "bg-muted text-foreground"
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-3 pt-2 border-t border-gray-200 text-xs">
                          <p className="font-semibold mb-1">Sources:</p>
                          {message.sources.map((source, index) => (
                            <div key={index} className="mt-1 p-2 bg-background/50 rounded text-xs">
                              <div className="flex items-center mb-1">
                                <FileText className="h-3 w-3 mr-1" />
                                <span className="font-medium">Citation {index + 1}</span>
                              </div>
                              {source.text.substring(0, 150)}
                              {source.text.length > 150 ? '...' : ''}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      <span className="text-xs opacity-70 mt-2 block">
                        {message.timestamp.toLocaleTimeString("en-US", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>
                    {message.role === "user" && (
                      <div className="flex-shrink-0 w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                        <User className="h-4 w-4 text-secondary-foreground" />
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-3 justify-start">
                    <div className="flex-shrink-0 w-8 h-8 bg-education-blue rounded-full flex items-center justify-center">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div className="bg-muted rounded-lg px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm text-muted-foreground">
                          AI is thinking...
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            <div className="border-t border-border p-4">
              {documents.length > 0 && (
                <div className="flex items-center mb-3 gap-2">
                  <div className="flex-1">
                    <Select
                      value={selectedDocument || "no_doc"}
                      onValueChange={(value) => {
                        setSelectedDocument(value === "no_doc" ? null : value);
                        setIsDocumentMode(value !== "no_doc");
                      }}
                    >
                      <SelectTrigger className="w-full h-8 text-xs">
                        <SelectValue placeholder="Select document for Q&A..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="no_doc">No document</SelectItem>
                        {documents.map((doc) => (
                          <SelectItem key={doc.id} value={doc.id.toString()}>
                            {doc.originalName}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  {selectedDocument && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => {
                        setSelectedDocument(null);
                        setIsDocumentMode(false);
                      }}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              )}
              
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={isDocumentMode ? "Ask questions about the document..." : "Enter your question..."}
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  size="icon"
                  className="shrink-0"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                {isDocumentMode 
                  ? `Current document: ${documents.find(d => d.id.toString() === selectedDocument)?.originalName || ""}`
                  : "Press Enter to send, Shift + Enter for new line"}
              </p>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Chat;