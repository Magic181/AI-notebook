import api from './index'

export interface Conversation {
  id: number
  notebook_id: number
  title: string
  created_at: string
  updated_at: string
}

export interface DocumentCitation {
  source_type?: 'document'
  document_id: number
  document_name: string
  chunk_id: number
  chunk_text: string
  position: number
  document_source_type?: 'paragraph' | 'page' | 'table' | 'code' | 'image_ocr' | 'image_caption' | 'mixed' | 'text' | string
  metadata?: Record<string, unknown>
}

export interface WebCitation {
  source_type: 'web'
  title: string
  url: string
  content: string
  position: number
}

export type Citation = DocumentCitation | WebCitation
export type SearchMode = 'local' | 'web' | 'hybrid'

export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  citations: Citation[]
  created_at: string
}

export const chatApi = {
  listConversations: (notebookId: number) =>
    api.get<Conversation[]>(`/notebooks/${notebookId}/conversations/`),
  createConversation: (notebookId: number, title?: string) =>
    api.post<Conversation>(`/notebooks/${notebookId}/conversations/`, { title }),
  deleteConversation: (conversationId: number) =>
    api.delete(`/conversations/${conversationId}/`),
  listMessages: (conversationId: number) =>
    api.get<Message[]>(`/conversations/${conversationId}/messages/`),
  sendMessage: (
    conversationId: number,
    content: string,
    searchMode: SearchMode = 'local',
  ) =>
    api.post<{
      user_message: Message
      assistant_message: Message
    }>(`/conversations/${conversationId}/messages/send/`, {
      content,
      search_mode: searchMode,
    }),
}
