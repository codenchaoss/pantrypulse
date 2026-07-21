import { Component, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { AiAssistantService } from '../../../core/services/ai-assistant.service';
import { ChatMessage, ChatResponseDto } from '../../../core/models/chat-message.model';

@Component({
  selector: 'app-ai-chat',
  templateUrl: './ai-chat.component.html',
  styleUrls: ['./ai-chat.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AiChatComponent {
  title = 'AI Assistant';
  description = 'Your intelligent restaurant management companion powered by Spring Boot AI.';

  messages: ChatMessage[] = [];
  promptText: string = '';
  isTyping: boolean = false;
  errorMessage: string | null = null;
  lastFailedPrompt: string | null = null;

  suggestedPrompts: string[] = [
    'What ingredients expire tomorrow?',
    "Suggest today's special menu.",
    'Which items are low in stock?',
    'Show recipes using paneer.',
    'Recommend dishes under ₹2000 budget.'
  ];

  constructor(
    private aiAssistantService: AiAssistantService,
    private cdr: ChangeDetectorRef
  ) {}

  /**
   * Sends user message to backend Spring Boot API (POST /api/ai/chat)
   */
  sendMessage(textToSend?: string): void {
    const text = (textToSend || this.promptText).trim();
    if (!text || this.isTyping) {
      return;
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      status: 'sending'
    };

    this.messages.push(userMessage);
    this.promptText = '';
    this.isTyping = true;
    this.errorMessage = null;
    this.cdr.markForCheck();

    this.aiAssistantService.sendMessage(text).subscribe({
      next: (res: ChatResponseDto) => {
        userMessage.status = 'sent';
        this.isTyping = false;

        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: res.data?.answer || 'No response received from the AI Assistant.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          status: 'sent'
        };

        this.messages.push(aiMessage);
        this.cdr.markForCheck();
      },
      error: (err) => {
        userMessage.status = 'error';
        this.isTyping = false;
        this.lastFailedPrompt = text;

        if (err.status === 0) {
          this.errorMessage = 'Unable to connect to Spring Boot AI Chat service. Ensure the backend server is running and CORS is configured correctly.';
        } else if (err.status === 403) {
          this.errorMessage = 'AI Chat is currently unavailable or permission denied.';
        } else if (err.status === 404) {
          this.errorMessage = 'AI Chat endpoint (/api/ai/chat) not found on backend (HTTP 404).';
        } else if (err.status === 500) {
          this.errorMessage = 'The AI service is experiencing internal issues (HTTP 500). Please try again later.';
        } else if (err.error && err.error.message) {
          this.errorMessage = `Backend Error: ${err.error.message}`;
        } else {
          this.errorMessage = `Failed to get response from AI Assistant (HTTP Status: ${err.status || 'Unknown'}).`;
        }

        this.cdr.markForCheck();
      }
    });
  }

  /**
   * Triggers message sending when clicking a prompt chip
   */
  selectSuggestedPrompt(prompt: string): void {
    this.sendMessage(prompt);
  }

  /**
   * Resets conversation to empty state
   */
  clearChat(): void {
    this.messages = [];
    this.errorMessage = null;
    this.lastFailedPrompt = null;
    this.isTyping = false;
    this.promptText = '';
    this.cdr.markForCheck();
  }

  /**
   * Retries last failed prompt
   */
  retryLastMessage(): void {
    if (this.lastFailedPrompt) {
      const promptToRetry = this.lastFailedPrompt;
      this.errorMessage = null;
      this.sendMessage(promptToRetry);
    }
  }

  /**
   * Submits on Enter key press
   */
  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
}
