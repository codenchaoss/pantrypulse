export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
  status?: 'sending' | 'sent' | 'error';
  suggestedActions?: string[];
}

export interface ChatRequestDto {
  question: string;
  history?: string;
}


export interface ChatResponseDto {
  response?: string;
  message?: string;
  timestamp?: string;
  success?: boolean;
  data?: {
    answer?: string;
  };
}
