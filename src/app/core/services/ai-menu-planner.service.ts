import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { MenuResponseDto } from '../models/menu-response.dto';
import { MenuRequestDto } from '../models/menu-request.dto';

@Injectable({
  providedIn: 'root'
})
export class AiMenuPlannerService {
  private apiUrl = `${environment.apiUrl}/ai`;

  constructor(private http: HttpClient) {}

  /**
   * Fetches AI Menu recommendations from Spring Boot AiController (GET /api/ai/menu)
   */
  getMenuPlan(): Observable<MenuResponseDto> {
    return this.http.get<MenuResponseDto>(`${this.apiUrl}/menu`);
  }

  /**
   * Sends menu generation parameters if POST payload supported (POST /api/ai/menu)
   */
  generateMenuPlan(request?: MenuRequestDto): Observable<MenuResponseDto> {
    if (request && ((request.inventory && request.inventory.length > 0) || (request.recipes && request.recipes.length > 0))) {
      return this.http.post<MenuResponseDto>(`${this.apiUrl}/menu`, request);
    }
    return this.getMenuPlan();
  }
}
