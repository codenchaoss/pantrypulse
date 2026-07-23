import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { InventoryService } from '../../services/inventory.service';
import { AiAssistantService } from '../../core/services/ai-assistant.service';

@Component({
  selector: 'app-inventory',
  templateUrl: './inventory.component.html',
  styleUrls: ['./inventory.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class InventoryComponent implements OnInit {

  searchText: string = '';
  selectedCategory: string = '';
  selectedStockStatus: string = '';
  selectedExpiryStatus: string = '';

  ingredients: any[] = [];
  isLoading = true;

  // ── AI Optimization modal ──────────────────────────────────────────────────
  showOptimizationModal = false;
  isOptLoading = false;
  optError = '';
  optimizationData: any = null;

  // Stats Counters
  totalIngredients = 0;
  lowStockCount = 0;
  expiringSoonCount = 0;
  expiredCount = 0;

  constructor(
    private inventoryService: InventoryService,
    private aiAssistantService: AiAssistantService,
    public cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadIngredients();
  }

  loadIngredients(): void {
    this.isLoading = true;
    this.cdr.markForCheck();

    this.inventoryService.getIngredients().subscribe({
      next: (data) => {
        this.ingredients = data.map((item: any) => ({
          ...item,
          status: this.getStatus(item.expiryDate, item.available)
        }));
        this.calculateStats();
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error loading ingredients', err);
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    });
  }

  calculateStats(): void {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    this.totalIngredients = this.ingredients.length;
    this.lowStockCount = 0;
    this.expiringSoonCount = 0;
    this.expiredCount = 0;

    this.ingredients.forEach(item => {
      // 1. Low stock: quantity <= minimumStock
      if (item.quantity <= item.minimumStock) {
        this.lowStockCount++;
      }

      // 2. Expiry status
      if (item.expiryDate) {
        const expiry = new Date(item.expiryDate);
        expiry.setHours(0, 0, 0, 0);
        
        const diffTime = expiry.getTime() - today.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays < 0) {
          this.expiredCount++;
        } else if (diffDays <= 7) {
          this.expiringSoonCount++;
        }
      }
    });
  }

  deleteIngredient(id: number): void {
    if (confirm('Are you sure you want to delete this ingredient?')) {
      this.inventoryService.deleteIngredient(id).subscribe({
        next: () => {
          this.loadIngredients();
        },
        error: (err) => {
          console.error(err);
          alert('Failed to delete ingredient');
        }
      });
    }
  }

  getStatus(expiryDate: string, available: boolean): string {
    if (!available) {
      return 'Critical';
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const expiry = new Date(expiryDate);
    expiry.setHours(0, 0, 0, 0);

    const diffDays = Math.ceil(
      (expiry.getTime() - today.getTime()) /
      (1000 * 60 * 60 * 24)
    );

    if (diffDays < 0) {
      return 'Expired';
    }

    if (diffDays <= 2) {
      return 'Critical';
    }

    if (diffDays <= 7) {
      return 'Expiring Soon';
    }

    return 'Good';
  }

  getExpiryLabel(expiryDate: string): string {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const expiry = new Date(expiryDate);
    expiry.setHours(0, 0, 0, 0);

    const diffDays = Math.ceil(
      (expiry.getTime() - today.getTime()) /
      (1000 * 60 * 60 * 24)
    );

    if (diffDays < 0) {
      return 'Expired';
    } else if (diffDays === 0) {
      return 'Expires Today';
    } else if (diffDays === 1) {
      return 'Expires Tomorrow';
    } else if (diffDays <= 7) {
      return `Expires in ${diffDays} days`;
    }
    return expiry.toLocaleDateString();
  }

  get filteredIngredients() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return this.ingredients.filter(item => {
      // 1. Search text
      const matchesSearch = !this.searchText || 
        item.ingredientName?.toLowerCase().includes(this.searchText.toLowerCase());

      // 2. Category
      const matchesCategory = !this.selectedCategory || 
        item.category === this.selectedCategory;

      // 3. Stock status filter
      let matchesStock = true;
      if (this.selectedStockStatus === 'low') {
        matchesStock = item.quantity <= item.minimumStock;
      } else if (this.selectedStockStatus === 'normal') {
        matchesStock = item.quantity > item.minimumStock;
      }

      // 4. Expiry status filter
      let matchesExpiry = true;
      if (item.expiryDate) {
        const expiry = new Date(item.expiryDate);
        expiry.setHours(0, 0, 0, 0);
        const diffDays = Math.ceil((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

        if (this.selectedExpiryStatus === 'expired') {
          matchesExpiry = diffDays < 0;
        } else if (this.selectedExpiryStatus === 'expiring_soon') {
          matchesExpiry = diffDays >= 0 && diffDays <= 7;
        } else if (this.selectedExpiryStatus === 'good') {
          matchesExpiry = diffDays > 7;
        }
      }

      return matchesSearch && matchesCategory && matchesStock && matchesExpiry;
    });
  }


  getStockPercent(item: any): number {
    if (!item.minimumStock) return 100;
    const ratio = (item.quantity / (item.minimumStock * 2)) * 100;
    return Math.min(100, Math.max(0, ratio));
  }

  trackById(index: number, item: any): number {
    return item.id;
  }

  // ── AI Optimization modal ──────────────────────────────────────────────────
  getAiOptimization(): void {
    this.showOptimizationModal = true;
    this.isOptLoading = true;
    this.optError = '';
    this.optimizationData = null;
    this.cdr.markForCheck();

    const formattedItems = this.ingredients.map(item => {
      let days = 999;
      if (item.expiryDate) {
        const diffTime = new Date(item.expiryDate).getTime() - new Date().getTime();
        days = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        if (isNaN(days)) days = 999;
      }
      return {
        ingredient: item.ingredientName,
        quantity: item.quantity ? Math.round(item.quantity) : 0,
        unit: item.unit || '',
        expiry_days: days
      };
    });

    this.aiAssistantService.optimizeInventory(formattedItems).subscribe({
      next: (res) => {
        this.isOptLoading = false;
        if (res && res.success && res.data) {
          this.optimizationData = res.data;
        } else {
          this.optError = res.message || 'Failed to generate inventory optimization recommendations.';
        }
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.isOptLoading = false;
        this.optError = 'AI Optimization service is currently unavailable. Ensure the AI profile is enabled on the backend.';
        console.error('AI Optimization error:', err);
        this.cdr.markForCheck();
      }
    });
  }

  closeOptimizationModal(): void {
    this.showOptimizationModal = false;
    this.optimizationData = null;
    this.optError = '';
    this.cdr.markForCheck();
  }
}