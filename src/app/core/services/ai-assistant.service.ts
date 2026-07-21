import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ChatRequestDto, ChatResponseDto } from '../models/chat-message.model';

@Injectable({
  providedIn: 'root'
})
export class AiAssistantService {
  private apiUrl = `${environment.apiUrl}/ai`;

  constructor(private http: HttpClient) { }

  /**
   * Sends user prompt to Spring Boot AI Assistant API (POST /api/ai/chat)
   */
  sendMessage(prompt: string): Observable<ChatResponseDto> {

    const payload: ChatRequestDto = {
      question: prompt,
      history: ""
    };

    return this.http.post<ChatResponseDto>(
      `${this.apiUrl}/chat`,
      payload
    );
  }
}
