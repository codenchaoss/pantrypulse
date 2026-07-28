import { Component, OnInit, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { HistoricalOrderService } from '../../core/services/historical-order.service';
import { RecipeService } from '../../core/services/recipe.service';
import { HistoricalOrder } from '../../core/models/historical-order.model';
import { Recipe } from '../../core/models/recipe.model';
import { HistoricalOrderDialogComponent } from './historical-order-dialog.component';
import { ToastService } from 'src/app/shared/toast.service';
@Component({
  selector: 'app-historical-orders',
  templateUrl: './historical-orders.component.html',
  styleUrls: ['./historical-orders.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HistoricalOrdersComponent implements OnInit {
  orders: HistoricalOrder[] = [];
  filteredOrders: HistoricalOrder[] = [];
  recipes: Recipe[] = [];
  recipesMap = new Map<number, Recipe>();

  displayedColumns: string[] = ['recipeName', 'quantity', 'orderDate', 'actions'];
  searchText = '';
  filterDate = '';
  isLoading = false;
  isConnectionError = false;

  // Stats Counters
  totalRecords = 0;
  totalQuantity = 0;
  mostOrderedRecipe = 'N/A';

  constructor(
    private orderService: HistoricalOrderService,
    private recipeService: RecipeService,
    private dialog: MatDialog,
    private cdr: ChangeDetectorRef,
    private toast:ToastService
  ) {}

  ngOnInit(): void {
    this.loadInitialData();
  }

  loadInitialData(): void {
    this.isLoading = true;
    this.isConnectionError = false;
    this.cdr.markForCheck();

    // First load recipes, then orders
    this.recipeService.getAllRecipes(0, 1000).subscribe({
      next: (res) => {
        this.recipes = res.content || [];
        this.recipesMap = new Map(this.recipes.map(r => [r.id!, r]));
        this.loadOrders();
      },
      error: (err) => {
        console.error('Error loading recipes:', err);
        // Proceed to load orders even if recipes load fails
        this.loadOrders();
      }
    });
  }

  loadOrders(): void {
    this.isLoading = true;
    this.cdr.markForCheck();

    this.orderService.getHistoricalOrders().subscribe({
      next: (data) => {
        this.orders = data || [];
        this.applyFilters();
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error loading historical orders:', err);
        this.isLoading = false;
        if (err.status === 0) {
          this.isConnectionError = true;
        }
        this.cdr.markForCheck();
      }
    });
  }

  calculateStats(): void {
    this.totalRecords = this.orders.length;
    
    let quantitySum = 0;
    const recipeQuantities = new Map<number | string, number>();

    this.orders.forEach(order => {
      quantitySum += order.quantity;
      
      const recipeId = order.recipeId;
      const name = order.recipeName || this.recipesMap.get(recipeId)?.recipeName || 'Unknown Recipe';
      
      const currentQty = recipeQuantities.get(name) || 0;
      recipeQuantities.set(name, currentQty + order.quantity);
    });

    this.totalQuantity = quantitySum;

    // Find the recipe with the highest cumulative quantity
    let maxQty = -1;
    let popularRecipe = 'N/A';
    recipeQuantities.forEach((qty, name) => {
      if (qty > maxQty) {
        maxQty = qty;
        popularRecipe = String(name);
      }
    });
    this.mostOrderedRecipe = popularRecipe;
  }

  applyFilters(): void {
    let result = [...this.orders];

    // Filter by search text (Recipe Name)
    if (this.searchText.trim()) {
      const search = this.searchText.toLowerCase().trim();
      result = result.filter(order => {
        const rName = (order.recipeName || this.getRecipeName(order.recipeId)).toLowerCase();
        return rName.includes(search);
      });
    }

    // Filter by order date
    if (this.filterDate) {
      result = result.filter(order => {
        if (!order.orderDate) return false;
        // Compare dates (YYYY-MM-DD)
        const oDate = order.orderDate.substring(0, 10);
        return oDate === this.filterDate;
      });
    }

    this.filteredOrders = result;
    this.calculateStats();
    this.cdr.markForCheck();
  }

  getRecipeName(recipeId: number): string {
    return this.recipesMap.get(recipeId)?.recipeName || `Recipe #${recipeId}`;
  }

  clearDateFilter(): void {
    this.filterDate = '';
    this.applyFilters();
  }

  openAddDialog(): void {
    const dialogRef = this.dialog.open(HistoricalOrderDialogComponent, {
      width: '600px',
      data: { mode: 'add', recipes: this.recipes },
      disableClose: true
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadOrders();
      }
    });
  }

  openViewDialog(order: HistoricalOrder): void {
    this.dialog.open(HistoricalOrderDialogComponent, {
      width: '600px',
      data: { mode: 'view', orderId: order.id, recipesMap: this.recipesMap },
      disableClose: false
    });
  }

  deleteOrder(id: number, recipeId: number): void {
    const recipeName = this.getRecipeName(recipeId);
    if (confirm(`Are you sure you want to delete historical record for "${recipeName}"?`)) {
      this.isLoading = true;
      this.cdr.markForCheck();

      this.orderService.deleteHistoricalOrder(id).subscribe({
        next: () => {
          this.loadOrders();
        },
        error: (err) => {
          console.error('Error deleting historical order:', err);
          this.isLoading = false;
          if (err.status === 0) {
            this.isConnectionError = true;
          } else {
            this.toast.error(
    'Delete Failed',
    'Unable to delete historical order.'
);
          }
          this.cdr.markForCheck();
        }
      });
    }
  }
}
