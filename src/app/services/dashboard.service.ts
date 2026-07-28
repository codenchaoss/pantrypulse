import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface DashboardSummaryResponse {
  totalIngredients: number;
  totalRecipes: number;
  lowStockItems: number;
  expiringSoon: number;
  expiredItems: number;
  recentIngredients: Array<{
    ingredient: string;
    quantity: number;
    expiry: string;
    status: string;
  }>;
  recentRecipes: Array<{
    recipeName: string;
    category: string;
    prepTime: string;
    status: string;
  }>;
  expiryAlerts: Array<{
    ingredient: string;
    quantity: number;
    alertStatus: string;
  }>;
}

export interface DashboardData {
  totalIngredients: number;
  totalRecipes: number;
  lowStockCount: number;
  expiringSoonCount: number;
  expiredCount: number;
  recentIngredients: any[];
  recentRecipes: any[];
  expiryAlerts: any[];
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private apiUrl = `${environment.apiUrl}/api/dashboard/summary`;

  constructor(private http: HttpClient) {}

  getDashboardData(): Observable<DashboardData> {
    return this.http.get<DashboardSummaryResponse>(this.apiUrl).pipe(
      map((res: DashboardSummaryResponse) => {
        return {
          totalIngredients: res.totalIngredients || 0,
          totalRecipes: res.totalRecipes || 0,
          lowStockCount: res.lowStockItems || 0,
          expiringSoonCount: res.expiringSoon || 0,
          expiredCount: res.expiredItems || 0,
          recentIngredients: (res.recentIngredients || []).map((item, idx) => ({
            id: idx + 1,
            ingredientName: item.ingredient,
            quantity: item.quantity,
            unit: '',
            expiryDate: item.expiry,
            stockStatus: item.status
          })),
          recentRecipes: (res.recentRecipes || []).map((recipe, idx) => ({
            id: idx + 1,
            recipeName: recipe.recipeName,
            category: recipe.category,
            preparationTime: recipe.prepTime,
            available: recipe.status === 'Available'
          })),
          expiryAlerts: (res.expiryAlerts || []).map(alert => ({
            ingredientName: alert.ingredient,
            quantity: alert.quantity,
            statusText: alert.alertStatus,
            badgeClass: alert.alertStatus === 'Expired' ? 'danger' : alert.alertStatus === 'Expiring Soon' ? 'warning' : 'info'
          }))
        };
      })
    );
  }
}
