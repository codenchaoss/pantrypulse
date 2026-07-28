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
  private apiUrl = `${environment.apiUrl}/api/ai`;

  constructor(private http: HttpClient) {}

  /**
   * Fetches AI Menu recommendations from Spring Boot AiController (GET /api/ai/menu)
   */
  getMenuPlan(): Observable<MenuResponseDto> {
    return this.http.get<MenuResponseDto>(`${this.apiUrl}/menu`);
  }

  /**
   * Generates menu plan using the AI endpoint (GET /api/ai/menu only as per requirements)
   */
  generateMenuPlan(request?: MenuRequestDto): Observable<MenuResponseDto> {
    return this.getMenuPlan();
  }
}
