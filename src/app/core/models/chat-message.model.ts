export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
  status?: 'sending' | 'sent' | 'error';
  suggestedActions?: string[];
}

export interface ChatRequestDto {
  prompt: string;
  conversationId?: string;
}

export interface ChatResponseDto {
  response?: string;
  message?: string;
  timestamp?: string;
  success?: boolean;
}
