import { Injectable } from '@angular/core';
import { forkJoin, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { InventoryService } from './inventory.service';
import { RecipeService } from '../core/services/recipe.service';

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

  constructor(
    private inventoryService: InventoryService,
    private recipeService: RecipeService
  ) {}

  getDashboardData(): Observable<DashboardData> {
    return forkJoin({
      ingredients: this.inventoryService.getIngredients(),
      recipesResponse: this.recipeService.getAllRecipes(0, 1000)
    }).pipe(
      map(({ ingredients, recipesResponse }) => {
        const recipes = recipesResponse.content || [];
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        // 1. Stats calculations
        let lowStockCount = 0;
        let expiringSoonCount = 0;
        let expiredCount = 0;
        const expiryAlerts: any[] = [];

        ingredients.forEach(item => {
          // Low stock check
          if (item.quantity <= item.minimumStock) {
            lowStockCount++;
          }

          // Expiry status checks
          if (item.expiryDate) {
            const expiry = new Date(item.expiryDate);
            expiry.setHours(0, 0, 0, 0);
            const diffDays = Math.ceil((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

            if (diffDays < 0) {
              expiredCount++;
              expiryAlerts.push({
                ingredientName: item.ingredientName,
                quantity: `${item.quantity} ${item.unit}`,
                statusText: 'Expired',
                badgeClass: 'danger',
                sortOrder: 0
              });
            } else if (diffDays === 0) {
              expiringSoonCount++;
              expiryAlerts.push({
                ingredientName: item.ingredientName,
                quantity: `${item.quantity} ${item.unit}`,
                statusText: 'Expiring Today',
                badgeClass: 'danger',
                sortOrder: 1
              });
            } else if (diffDays <= 3) {
              expiringSoonCount++;
              expiryAlerts.push({
                ingredientName: item.ingredientName,
                quantity: `${item.quantity} ${item.unit}`,
                statusText: `Expires in ${diffDays} days`,
                badgeClass: 'warning',
                sortOrder: 2
              });
            } else if (diffDays <= 7) {
              expiryAlerts.push({
                ingredientName: item.ingredientName,
                quantity: `${item.quantity} ${item.unit}`,
                statusText: `Expires in ${diffDays} days`,
                badgeClass: 'success',
                sortOrder: 3
              });
            }
          }
        });

        // Sort expiry alerts: Expired first, then Today, then Soon
        expiryAlerts.sort((a, b) => a.sortOrder - b.sortOrder);

        // 2. Recent Items (slice latest 5 sorted by ID descending)
        const recentIngredients = [...ingredients]
          .sort((a, b) => (b.id || 0) - (a.id || 0))
          .slice(0, 5)
          .map(item => ({
            ...item,
            stockStatus: item.quantity <= item.minimumStock ? 'Low Stock' : 'Good'
          }));

        const recentRecipes = [...recipes]
          .sort((a, b) => (b.id || 0) - (a.id || 0))
          .slice(0, 5);

        return {
          totalIngredients: ingredients.length,
          totalRecipes: recipes.length,
          lowStockCount,
          expiringSoonCount, // Expiring today or within 7 days
          expiredCount,
          recentIngredients,
          recentRecipes,
          expiryAlerts: expiryAlerts.slice(0, 5) // Limit to top 5 alert items
        };
      })
    );
  }
}
