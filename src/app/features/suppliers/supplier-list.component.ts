import { Component, OnInit, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { SupplierService } from '../../services/supplier.service';
import { Supplier } from '../../core/models/supplier.model';
import { SupplierDialogComponent } from './supplier-dialog.component';

@Component({
  selector: 'app-supplier-list',
  templateUrl: './supplier-list.component.html',
  styleUrls: ['./supplier-list.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SupplierListComponent implements OnInit {

  suppliers: Supplier[] = [];
  filteredSuppliers: Supplier[] = [];
  displayedColumns: string[] = ['supplierName', 'contactPerson', 'phone', 'email', 'status', 'actions'];
  searchText = '';
  isLoading = false;
  isConnectionError = false;

  constructor(
    private supplierService: SupplierService,
    private dialog: MatDialog,
    public cdr: ChangeDetectorRef
  ) { }

  ngOnInit(): void {
    this.loadSuppliers();
  }

  loadSuppliers(): void {
    this.isLoading = true;
    this.isConnectionError = false;
    this.cdr.markForCheck();

    this.supplierService.getSuppliers().subscribe({
      next: (data) => {
        this.suppliers = data || [];
        this.applyFilter();
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error fetching suppliers:', err);
        this.isLoading = false;
        // Only trigger backend connection message on status 0 / connection refused / network error
        if (err.status === 0) {
          this.isConnectionError = true;
        }
        this.cdr.markForCheck();
      }
    });
  }

  applyFilter(): void {
    if (!this.searchText.trim()) {
      this.filteredSuppliers = [...this.suppliers];
    } else {
      const keyword = this.searchText.toLowerCase().trim();
      this.filteredSuppliers = this.suppliers.filter(s =>
        s.supplierName.toLowerCase().includes(keyword) ||
        s.contactPerson.toLowerCase().includes(keyword) ||
        (s.email && s.email.toLowerCase().includes(keyword)) ||
        s.phone.includes(keyword)
      );
    }
    this.cdr.markForCheck();
  }

  onSearchChange(): void {
    this.applyFilter();
  }

  openAddDialog(): void {
    const dialogRef = this.dialog.open(SupplierDialogComponent, {
      width: '600px',
      data: { mode: 'add' },
      disableClose: true
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadSuppliers();
      }
    });
  }

  openViewDialog(supplier: Supplier): void {
    this.dialog.open(SupplierDialogComponent, {
      width: '600px',
      data: { mode: 'view', supplier },
      disableClose: false
    });
  }

  openEditDialog(supplier: Supplier): void {
    const dialogRef = this.dialog.open(SupplierDialogComponent, {
      width: '600px',
      data: { mode: 'edit', supplier },
      disableClose: true
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadSuppliers();
      }
    });
  }

  deleteSupplier(id: number, name: string): void {
    if (confirm(`Are you sure you want to delete supplier "${name}"?`)) {
      this.isLoading = true;
      this.cdr.markForCheck();

      this.supplierService.deleteSupplier(id).subscribe({
        next: () => {
          this.loadSuppliers();
        },
        error: (err) => {
          console.error('Error deleting supplier:', err);
          this.isLoading = false;
          if (err.status === 0) {
            this.isConnectionError = true;
          }
          this.cdr.markForCheck();
        }
      });
    }
  }
}
