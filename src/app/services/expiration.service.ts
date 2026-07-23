import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ExpiringIngredient {
  inventoryId: number;
  ingredientName: string;
  quantity: number;
  unit: string;
  expiryDate: string;
  daysRemaining: number;
  category?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ExpirationService {

  private apiUrl = `${environment.apiUrl}/expiration/expiring`;

  constructor(private http: HttpClient) { }

  getExpiringIngredients(): Observable<ExpiringIngredient[]> {
    return this.http.get<ExpiringIngredient[]>(this.apiUrl);
  }
}
