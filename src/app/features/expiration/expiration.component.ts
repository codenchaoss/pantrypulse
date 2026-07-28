import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';

import { ExpirationService } from './services/expiration.service';
import { ExpiringIngredient } from './models/expiration.model';

@Component({
  selector: 'app-expiration',
  templateUrl: './expiration.component.html',
  styleUrls: ['./expiration.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ExpirationComponent implements OnInit {

  ingredients: ExpiringIngredient[] = [];

  filteredIngredients: ExpiringIngredient[] = [];

  searchText = '';

  isLoading = true;

  totalExpiring = 0;

  expiringToday = 0;

  expiringTomorrow = 0;

  expiringWeek = 0;
  expiredCount = 0;

  healthyCount = 0;

  selectedFilter = 'ALL';

  constructor(
    private expirationService: ExpirationService,
    public cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {

  this.loadIngredients();

}

getEmptyMessage(): string {

  switch (this.selectedFilter) {

    case 'CRITICAL':
      return '🎉No critical ingredients found.';

    case 'EXPIRED':
      return 'No expired ingredients found.';

    case 'GOOD':
      return 'No healthy ingredients found.';

    default:
      return 'No ingredients are expiring soon.';
  }

}
 loadIngredients(): void {

  this.isLoading = true;

  this.expirationService.getExpiringIngredients().subscribe({

    next: (data) => {

      this.ingredients = data;

      this.filteredIngredients = data;

      this.calculateStats();

      this.isLoading = false;

      this.cdr.markForCheck();

    },

    error: (err) => {

      console.error(err);

      this.isLoading = false;

      this.cdr.markForCheck();

    }

  });

}
filterIngredients(): void {

  this.applyFilters();

}
onSearch(event: Event): void {

  const target = event.target as HTMLInputElement;

  this.searchText = target.value;

  if (this.searchText.trim().length < 2) {

    this.filteredIngredients = [...this.ingredients];
    return;

  }

  this.filterIngredients();

}

  calculateStats(): void {

  this.totalExpiring = this.ingredients.length;

  this.expiredCount = this.ingredients.filter(

    i => i.daysRemaining < 0

  ).length;

  this.healthyCount = this.ingredients.filter(

    i => i.daysRemaining > 7

  ).length;

}

getStatus(days: number): string {

  if (days < 0) {
    return 'Expired';
  }

  if (days <= 3) {
    return 'Critical';
  }

  if (days <= 7) {
    return 'Expiring Soon';
  }

  return 'Good';
}
filterByStatus(status: string): void {

  this.selectedFilter = status;

  this.applyFilters();

}
applyFilters(): void {

  let data = [...this.ingredients];

  
  if (this.searchText.trim().length >= 2) {

    const keyword = this.searchText.toLowerCase();

    data = data.filter(item =>
      item.ingredientName.toLowerCase().includes(keyword)
    );

  }

  
  switch (this.selectedFilter) {

    case 'CRITICAL':
      data = data.filter(i =>
        i.daysRemaining >= 0 &&
        i.daysRemaining <= 3
      );
      break;

    case 'EXPIRED':
      data = data.filter(i =>
        i.daysRemaining < 0
      );
      break;

    case 'GOOD':
      data = data.filter(i =>
        i.daysRemaining > 7
      );
      break;

    default:
      break;
  }

  this.filteredIngredients = data;

}

}