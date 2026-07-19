import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { SupplierService } from '../../services/supplier.service';
import { Supplier } from '../../core/models/supplier.model';

interface DialogData {
  mode: 'add' | 'edit' | 'view';
  supplier?: Supplier;
}

@Component({
  selector: 'app-supplier-dialog',
  templateUrl: './supplier-dialog.component.html',
  styleUrls: ['./supplier-dialog.component.css']
})
export class SupplierDialogComponent implements OnInit {

  mode: 'add' | 'edit' | 'view';
  supplierForm: FormGroup;
  title = '';
  isSaving = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private supplierService: SupplierService,
    private dialogRef: MatDialogRef<SupplierDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: DialogData
  ) {
    this.mode = data.mode;
    
    // Initialize form controls
    this.supplierForm = this.fb.group({
      supplierName: ['', Validators.required],
      contactPerson: ['', Validators.required],
      phone: ['', Validators.required],
      email: ['', [Validators.email]],
      address: [''],
      gstNumber: ['', Validators.required],
      active: [true, Validators.required]
    });

    if (this.mode === 'view') {
      this.supplierForm.disable();
    }
  }

  ngOnInit(): void {
    // Populate form if view/edit mode
    if ((this.mode === 'edit' || this.mode === 'view') && this.data.supplier) {
      this.supplierForm.patchValue({
        supplierName: this.data.supplier.supplierName,
        contactPerson: this.data.supplier.contactPerson,
        phone: this.data.supplier.phone,
        email: this.data.supplier.email || '',
        address: this.data.supplier.address || '',
        gstNumber: this.data.supplier.gstNumber,
        active: this.data.supplier.active
      });
    }

    // Set dialog title
    if (this.mode === 'add') {
      this.title = 'Add New Supplier';
    } else if (this.mode === 'edit') {
      this.title = 'Edit Supplier';
    } else {
      this.title = 'Supplier Details';
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  onSave(): void {
    if (this.supplierForm.invalid) {
      this.markFormGroupTouched(this.supplierForm);
      return;
    }

    this.isSaving = true;
    this.errorMessage = '';
    const formValue = this.supplierForm.value;

    if (this.mode === 'add') {
      this.supplierService.addSupplier(formValue).subscribe({
        next: () => {
          this.isSaving = false;
          this.dialogRef.close(true);
        },
        error: (err) => {
          console.error('Error adding supplier:', err);
          this.isSaving = false;
          if (err.error && err.error.message) {
            this.errorMessage = err.error.message;
          } else {
            this.errorMessage = 'Failed to create supplier. Ensure Spring Boot is running.';
          }
        }
      });
    } else if (this.mode === 'edit' && this.data.supplier?.id) {
      this.supplierService.updateSupplier(this.data.supplier.id, formValue).subscribe({
        next: () => {
          this.isSaving = false;
          this.dialogRef.close(true);
        },
        error: (err) => {
          console.error('Error updating supplier:', err);
          this.isSaving = false;
          if (err.error && err.error.message) {
            this.errorMessage = err.error.message;
          } else {
            this.errorMessage = 'Failed to update supplier. Ensure Spring Boot is running.';
          }
        }
      });
    }
  }

  // Helper method to mark all form controls as touched to trigger validation messages
  private markFormGroupTouched(formGroup: FormGroup) {
    Object.values(formGroup.controls).forEach(control => {
      control.markAsTouched();
      if ((control as any).controls) {
        this.markFormGroupTouched(control as FormGroup);
      }
    });
  }
}
