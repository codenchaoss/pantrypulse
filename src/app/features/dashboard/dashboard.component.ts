import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { Subject, timer, forkJoin } from 'rxjs';
import { catchError, switchMap, takeUntil, map } from 'rxjs/operators';
import { DashboardData, DashboardService } from '../../services/dashboard.service';
import { ExpirationService, ExpiringIngredient } from '../../services/expiration.service';
import { InventoryService } from '../../services/inventory.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DashboardComponent implements OnInit, OnDestroy {

  data: DashboardData | null = null;
  expiringIngredients: ExpiringIngredient[] = [];
  isLoading = true;
  errorMessage = '';
  aiSuggestionsText = '';

  private destroy$ = new Subject<void>();
  private refreshTrigger$ = new Subject<void>();

  constructor(
    private dashboardService: DashboardService,
    private expirationService: ExpirationService,
    private inventoryService: InventoryService,
    public cdr: ChangeDetectorRef
  ) {}

  private fetchDashboardDetails() {
    return forkJoin({
      dashboard: this.dashboardService.getDashboardData(),
      expiring: this.expirationService.getExpiringIngredients(),
      inventory: this.inventoryService.getIngredients()
    }).pipe(
      map(({ dashboard, expiring, inventory }) => {
        const expiringWithCategory = expiring.map(exp => {
          const matched = inventory.find((inv: any) => 
            inv.id === exp.inventoryId || 
            (inv.ingredientName && exp.ingredientName && inv.ingredientName.toLowerCase() === exp.ingredientName.toLowerCase())
          );
          return {
            ...exp,
            category: matched ? matched.category : 'Others'
          };
        });
        this.expiringIngredients = expiringWithCategory;
        return dashboard;
      })
    );
  }

  getExpirationStatus(days: number): { text: string; class: string } {
    if (days <= 3) {
      return { text: '🔴 Critical', class: 'danger' };
    } else if (days <= 7) {
      return { text: '🟠 Warning', class: 'warning' };
    } else {
      return { text: '🟢 Safe', class: 'success' };
    }
  }

  ngOnInit(): void {
    // 60-second automatic refresh timer combined with manual refresh trigger
    timer(0, 60000).pipe(
      takeUntil(this.destroy$),
      switchMap(() => {
        this.isLoading = true;
        this.errorMessage = '';
        this.cdr.markForCheck();
        return this.fetchDashboardDetails().pipe(
          catchError(err => {
            console.error('Error in automatic dashboard fetch:', err);
            this.errorMessage = 'Failed to load dashboard data. Ensure backend is running.';
            this.isLoading = false;
            this.cdr.markForCheck();
            throw err;
          })
        );
      })
    ).subscribe({
      next: (dashboardData: DashboardData) => {
        this.data = dashboardData;
        this.updateAiSuggestions();
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        // Handled in catchError
      }
    });

    // Manual refresh subscriber
    this.refreshTrigger$.pipe(
      takeUntil(this.destroy$),
      switchMap(() => {
        this.isLoading = true;
        this.errorMessage = '';
        this.cdr.markForCheck();
        return this.fetchDashboardDetails().pipe(
          catchError(err => {
            console.error('Error in manual dashboard fetch:', err);
            this.errorMessage = 'Failed to refresh dashboard. Check connection.';
            this.isLoading = false;
            this.cdr.markForCheck();
            throw err;
          })
        );
      })
    ).subscribe({
      next: (dashboardData: DashboardData) => {
        this.data = dashboardData;
        this.updateAiSuggestions();
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  triggerRefresh(): void {
    this.refreshTrigger$.next();
  }

  private updateAiSuggestions(): void {
    if (this.data && this.data.recentRecipes && this.data.recentRecipes.length > 0) {
      const names = this.data.recentRecipes.slice(0, 3).map(r => r.recipeName);
      if (names.length === 1) {
        this.aiSuggestionsText = `Based on today's inventory, prepare ${names[0]} to reduce food waste and maximize profit.`;
      } else if (names.length === 2) {
        this.aiSuggestionsText = `Based on today's inventory, prepare ${names[0]} and ${names[1]} to reduce food waste and maximize profit.`;
      } else {
        const last = names.pop();
        this.aiSuggestionsText = `Based on today's inventory, prepare ${names.join(', ')} and ${last} to reduce food waste and maximize profit.`;
      }
    } else {
      this.aiSuggestionsText = "Based on today's inventory, prepare Tomato Pasta, Vegetable Soup and Cheese Sandwiches to reduce food waste and maximize profit.";
    }
  }

  getCategoryLabel(category: string): string {
    if (!category) return 'Others';
    return category.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  trackByIngredient(index: number, item: any): number {
    return item.id;
  }

  trackByRecipe(index: number, item: any): number {
    return item.id;
  }
}
