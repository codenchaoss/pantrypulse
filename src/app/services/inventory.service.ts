import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class InventoryService {

 private apiUrl = `${environment.apiUrl}/api/inventory`;

  constructor(private http: HttpClient) { }

  getIngredients(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  getIngredientById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`);
  }

  addIngredient(ingredient: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, ingredient);
  }

  updateIngredient(id: number, ingredient: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${id}`, ingredient);
  }

  deleteIngredient(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }

  searchIngredient(keyword: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/search?name=${keyword}`);
  }

  getByCategory(category: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/category/${category}`);
  }
}