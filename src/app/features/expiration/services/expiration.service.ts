import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { ExpiringIngredient } from '../models/expiration.model';

@Injectable({
  providedIn: 'root'
})
export class ExpirationService {

  private apiUrl = `${environment.apiUrl}/api/expiration`;

  constructor(private http: HttpClient) {}

  getExpiringIngredients(): Observable<ExpiringIngredient[]> {
    return this.http.get<ExpiringIngredient[]>(
      `${this.apiUrl}/expiring`
    );
  }

}