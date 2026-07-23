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

  /**
   * Fetches AI Price recommendations from Spring Boot PricingAiController (POST /api/ai/pricing)
   */
  suggestPricing(dish: string, ingredientCost: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/pricing`, {
      dish,
      ingredient_cost: ingredientCost
    });
  }

  /**
   * Fetches AI Inventory Optimization from Spring Boot OptimizationAiController (POST /api/ai/optimization)
   */
  optimizeInventory(inventoryItems: any[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/optimization`, {
      inventory: inventoryItems
    });
  }

  /**
   * Generates a recipe based on selected ingredients (POST /api/ai/recipe)
   */
  generateRecipe(ingredients: string[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/recipe`, {
      ingredients: ingredients
    });
  }

  /**
   * Fetches AI Supplier Recommendations (POST /api/ai/supplier)
   */
  suggestSuppliers(payload: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/supplier`, payload);
  }
}
