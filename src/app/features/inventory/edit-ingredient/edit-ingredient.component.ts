import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { InventoryService } from '../../../services/inventory.service';

@Component({
  selector: 'app-edit-ingredient',
  templateUrl: './edit-ingredient.component.html',
  styleUrls: ['./edit-ingredient.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class EditIngredientComponent implements OnInit {

  id!: number;

  ingredient = {
    id: 0,
    ingredientName: '',
    quantity: 1,
    unit: '',
    category: '',
    expiryDate: '',
    minimumStock: 1,
    available: true
  };

  isSaving = false;
  errorMessage = '';
  backendErrors: { [key: string]: string } = {};

  constructor(
    private inventoryService: InventoryService,
    private route: ActivatedRoute,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.id = Number(this.route.snapshot.paramMap.get('id'));

    this.inventoryService.getIngredientById(this.id).subscribe({
      next: (data) => {
        this.ingredient = data;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = 'Unable to load ingredient details.';
        this.cdr.markForCheck();
      }
    });
  }

  updateIngredient(): void {
    this.isSaving = true;
    this.errorMessage = '';
    this.backendErrors = {};
    this.cdr.markForCheck();

    // Frontend validation check
    if (!this.ingredient.ingredientName.trim()) {
      this.backendErrors['ingredientName'] = 'Ingredient name is required';
    }
    if (!this.ingredient.category) {
      this.backendErrors['category'] = 'Category is required';
    }
    if (!this.ingredient.unit) {
      this.backendErrors['unit'] = 'Unit is required';
    }
    if (this.ingredient.quantity <= 0) {
      this.backendErrors['quantity'] = 'Quantity must be greater than zero';
    }
    if (this.ingredient.minimumStock <= 0) {
      this.backendErrors['minimumStock'] = 'Minimum stock must be greater than zero';
    }
    if (!this.ingredient.expiryDate) {
      this.backendErrors['expiryDate'] = 'Expiry date is required';
    } else {
      const expiry = new Date(this.ingredient.expiryDate);
      expiry.setHours(0,0,0,0);
      const today = new Date();
      today.setHours(0,0,0,0);
      if (expiry <= today) {
        this.backendErrors['expiryDate'] = 'Expiry date must be in the future';
      }
    }

    if (Object.keys(this.backendErrors).length > 0) {
      this.isSaving = false;
      this.errorMessage = 'Please fix the errors below.';
      this.cdr.markForCheck();
      return;
    }

    this.inventoryService.updateIngredient(this.id, this.ingredient).subscribe({
      next: () => {
        this.isSaving = false;
        this.router.navigate(['/inventory']);
      },
      error: (err) => {
        console.error(err);
        this.isSaving = false;

        if (err.status === 400 && err.error && err.error.errors) {
          this.errorMessage = 'Backend validation failed. Please check fields below.';
          err.error.errors.forEach((e: any) => {
            if (e.field) {
              this.backendErrors[e.field] = e.defaultMessage;
            }
          });
        } else {
          this.errorMessage = err.error?.message || 'Failed to update ingredient.';
        }
        this.cdr.markForCheck();
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/inventory']);
  }
}