import { Component, Inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { HistoricalOrderService } from '../../core/services/historical-order.service';
import { HistoricalOrder } from '../../core/models/historical-order.model';
import { Recipe } from '../../core/models/recipe.model';

interface DialogData {
  mode: 'add' | 'view';
  orderId?: number;
  recipes?: Recipe[];
  recipesMap?: Map<number, Recipe>;
}

@Component({
  selector: 'app-historical-order-dialog',
  templateUrl: './historical-order-dialog.component.html',
  styleUrls: ['./historical-order-dialog.component.css']
})
export class HistoricalOrderDialogComponent implements OnInit {
  mode: 'add' | 'view';
  orderForm: FormGroup;
  title = '';
  isSaving = false;
  isLoadingDetails = false;
  errorMessage = '';
  recipes: Recipe[] = [];

  constructor(
    private fb: FormBuilder,
    private orderService: HistoricalOrderService,
    private dialogRef: MatDialogRef<HistoricalOrderDialogComponent>,
    private cdr: ChangeDetectorRef,
    @Inject(MAT_DIALOG_DATA) public data: DialogData
  ) {
    this.mode = data.mode;
    this.recipes = data.recipes || [];

    // Initialize Form Group
    this.orderForm = this.fb.group({
      recipeId: ['', Validators.required],
      recipeName: [''], // Only used in view mode to display string
      quantity: ['', [Validators.required, Validators.min(1)]],
      orderDate: ['', Validators.required]
    });

    if (this.mode === 'view') {
      this.orderForm.disable();
    }
  }

  ngOnInit(): void {
    if (this.mode === 'add') {
      this.title = 'Add Historical Record';
      // Set default date to today
      const today = new Date().toISOString().substring(0, 10);
      this.orderForm.patchValue({ orderDate: today });
    } else if (this.mode === 'view') {
      this.title = 'Historical Record Details';
      if (this.data.orderId) {
        this.isLoadingDetails = true;
        this.cdr.markForCheck();

        this.orderService.getHistoricalOrderById(this.data.orderId).subscribe({
          next: (order) => {
            this.isLoadingDetails = false;
            const rName = order.recipeName || this.data.recipesMap?.get(order.recipeId)?.recipeName || `Recipe #${order.recipeId}`;
            this.orderForm.patchValue({
              recipeId: order.recipeId,
              recipeName: rName,
              quantity: order.quantity,
              orderDate: order.orderDate ? order.orderDate.substring(0, 10) : ''
            });
            this.cdr.markForCheck();
          },
          error: (err) => {
            console.error('Error fetching historical order details:', err);
            this.isLoadingDetails = false;
            this.errorMessage = 'Failed to load details. Ensure backend service is active.';
            this.cdr.markForCheck();
          }
        });
      }
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  onSave(): void {
    if (this.orderForm.invalid) {
      this.markFormGroupTouched(this.orderForm);
      return;
    }

    this.isSaving = true;
    this.errorMessage = '';
    this.cdr.markForCheck();

    const formValue = this.orderForm.value;
    const payload: HistoricalOrder = {
      recipeId: Number(formValue.recipeId),
      quantity: Number(formValue.quantity),
      orderDate: formValue.orderDate
    };

    this.orderService.addHistoricalOrder(payload).subscribe({
      next: () => {
        this.isSaving = false;
        this.dialogRef.close(true);
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error adding historical order:', err);
        this.isSaving = false;
        if (err.error && err.error.message) {
          this.errorMessage = err.error.message;
        } else if (err.status === 0) {
          this.errorMessage = 'Cannot connect to backend. Ensure server is running.';
        } else {
          this.errorMessage = 'Failed to add record. Please check validation rules.';
        }
        this.cdr.markForCheck();
      }
    });
  }

  private markFormGroupTouched(formGroup: FormGroup) {
    Object.values(formGroup.controls).forEach(control => {
      control.markAsTouched();
      if ((control as any).controls) {
        this.markFormGroupTouched(control as FormGroup);
      }
    });
  }
}
