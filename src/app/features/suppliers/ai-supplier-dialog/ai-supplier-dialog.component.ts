import { Component, OnInit, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { InventoryService } from '../../../services/inventory.service';
import { SupplierService } from '../../../services/supplier.service';
import { SettingsService } from '../../../core/services/settings.service';
import { AiAssistantService } from '../../../core/services/ai-assistant.service';

interface SupplierData {
  id: number;
  supplierName: string;
  contactPerson: string;
  phone: string;
  email: string;
}

interface InventoryIngredient {
  id: number;
  ingredientName: string;
  quantity: number;
  unit: string;
}

@Component({
  selector: 'app-ai-supplier-dialog',
  templateUrl: './ai-supplier-dialog.component.html',
  styleUrls: ['./ai-supplier-dialog.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AiSupplierDialogComponent implements OnInit {
  title = 'AI Supplier Assistant';
  
  step: 'form' | 'loading' | 'result' = 'form';
  
  supplierForm!: FormGroup;
  
  suppliersList: SupplierData[] = [];
  inventoryList: InventoryIngredient[] = [];
  filteredInventory: InventoryIngredient[] = [];
  selectedIngredients = new Set<string>();
  
  searchText = '';
  isLoadingPrefill = false;
  isSubmitting = false;
  errorMessage = '';

  aiResponse: any = null;

  urgencyLevels = [
    { label: 'Low', value: 'LOW', class: 'urgency-low' },
    { label: 'Medium', value: 'MEDIUM', class: 'urgency-medium' },
    { label: 'High', value: 'HIGH', class: 'urgency-high' },
    { label: 'Critical', value: 'CRITICAL', class: 'urgency-critical' }
  ];

  languages = [
    { label: 'English', value: 'English' },
    { label: 'Hindi', value: 'Hindi' },
    { label: 'Spanish', value: 'Spanish' },
    { label: 'French', value: 'French' }
  ];

  constructor(
    private fb: FormBuilder,
    private inventoryService: InventoryService,
    private supplierService: SupplierService,
    private settingsService: SettingsService,
    private aiAssistantService: AiAssistantService,
    private dialogRef: MatDialogRef<AiSupplierDialogComponent>,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.initForm();
    this.loadPrefillAndData();
  }

  initForm(): void {
    this.supplierForm = this.fb.group({
      supplier_name: [''],
      ingredient: ['', Validators.required],
      required_quantity: ['', Validators.required],
      required_date: ['', Validators.required],
      ingredients: [[]],
      restaurant_name: [''],
      contact_person: [''],
      supplier_email: ['', [Validators.email]],
      supplier_phone: [''],
      urgency_level: ['MEDIUM', Validators.required],
      language_preference: ['English']
    });
  }

  loadPrefillAndData(): void {
    this.isLoadingPrefill = true;
    this.cdr.markForCheck();

    // 1. Fetch Inventory Ingredients
    this.inventoryService.getIngredients().subscribe({
      next: (ingredients) => {
        this.inventoryList = (ingredients || []).map((item: any) => ({
          id: item.id,
          ingredientName: item.ingredientName,
          quantity: item.quantity,
          unit: item.unit
        }));
        this.filteredInventory = [...this.inventoryList];
        this.cdr.markForCheck();
      },
      error: (err) => console.error('Failed to load inventory for selector', err)
    });

    // 2. Fetch Suppliers for pre-fill selection
    this.supplierService.getSuppliers().subscribe({
      next: (suppliers) => {
        this.suppliersList = (suppliers || []).map((s: any) => ({
          id: s.id || 0,
          supplierName: s.supplierName || '',
          contactPerson: s.contactPerson || '',
          phone: s.phone || '',
          email: s.email || ''
        }));
        this.cdr.markForCheck();
      },
      error: (err) => console.error('Failed to load suppliers for list', err)
    });

    // 3. Fetch User profile to pre-fill restaurant details
    this.settingsService.getProfile().subscribe({
      next: (profile) => {
        if (profile) {
          this.supplierForm.patchValue({
            restaurant_name: profile.restaurantName || '',
            contact_person: profile.fullName || ''
          });
        }
        this.isLoadingPrefill = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Failed to load profile details', err);
        this.isLoadingPrefill = false;
        this.cdr.markForCheck();
      }
    });
  }

  onSupplierSelect(event: any): void {
    const selectedName = event.target.value;
    if (!selectedName) return;

    const matchedSupplier = this.suppliersList.find(s => s.supplierName === selectedName);
    if (matchedSupplier) {
      this.supplierForm.patchValue({
        supplier_name: matchedSupplier.supplierName,
        supplier_email: matchedSupplier.email || '',
        supplier_phone: matchedSupplier.phone || ''
      });
      this.cdr.markForCheck();
    }
  }

  applyFilter(): void {
    if (!this.searchText.trim()) {
      this.filteredInventory = [...this.inventoryList];
    } else {
      const q = this.searchText.toLowerCase().trim();
      this.filteredInventory = this.inventoryList.filter(i => 
        i.ingredientName.toLowerCase().includes(q)
      );
    }
    this.cdr.markForCheck();
  }

  toggleIngredient(name: string): void {
    if (this.selectedIngredients.has(name)) {
      this.selectedIngredients.delete(name);
    } else {
      this.selectedIngredients.add(name);
    }
    // Update Form value
    this.supplierForm.patchValue({
      ingredients: Array.from(this.selectedIngredients)
    });
    this.cdr.markForCheck();
  }

  onSubmit(): void {
    if (this.supplierForm.invalid) {
      this.supplierForm.markAllAsTouched();
      this.errorMessage = 'Please fill out all required fields with valid input.';
      this.cdr.markForCheck();
      return;
    }

    this.step = 'loading';
    this.errorMessage = '';
    this.cdr.markForCheck();

    const payload = this.supplierForm.value;

    this.aiAssistantService.suggestSuppliers(payload).subscribe({
      next: (res) => {
        this.step = 'result';
        try {
          this.aiResponse = this.parseAiResponse(res);
        } catch (e: any) {
          console.error(e);
          this.aiResponse = {
            isPlaintext: true,
            text: typeof res === 'string' ? res : (res.data || res.message || 'No clear recommendation text returned.')
          };
        }
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('AI Supplier Error:', err);
        this.step = 'form';
        if (err.status === 0) {
          this.errorMessage = 'Cannot connect to backend server. Make sure it is active.';
        } else {
          this.errorMessage = err.error?.message || `AI engine returned error code ${err.status}.`;
        }
        this.cdr.markForCheck();
      }
    });
  }

  parseAiResponse(res: any): any {
    if (!res) throw new Error('Empty response');

    let rawData = res.data;
    if (res.success && res.data) {
      rawData = res.data;
    } else if (typeof res === 'string') {
      rawData = res;
    } else if (res.message && !res.data) {
      rawData = res.message;
    }

    if (typeof rawData === 'string') {
      const trimmed = rawData.trim();
      let cleaned = trimmed;

      if (trimmed.startsWith('```')) {
        const matches = trimmed.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
        if (matches && matches[1]) {
          cleaned = matches[1].trim();
        }
      }

      try {
        const json = JSON.parse(cleaned);
        if (json) return this.mapStructuredResponse(json);
      } catch (e) {
        // plaintext format
        return {
          isPlaintext: true,
          text: trimmed
        };
      }
    }

    if (rawData && typeof rawData === 'object') {
      return this.mapStructuredResponse(rawData);
    }

    throw new Error('Unsupported AI format');
  }

  mapStructuredResponse(obj: any): any {
    return {
      isPlaintext: false,
      recommendedSupplier: obj.recommendedSupplier || obj.recommended_supplier || 'N/A',
      alternativeSuppliers: Array.isArray(obj.alternativeSuppliers) 
        ? obj.alternativeSuppliers 
        : Array.isArray(obj.alternatives) 
        ? obj.alternatives 
        : [],
      recommendedQuantity: obj.recommendedQuantity || obj.recommended_quantity || 'N/A',
      deliverySuggestions: obj.deliverySuggestions || obj.delivery_suggestions || 'N/A',
      costPricingNotes: obj.costPricingNotes || obj.cost_pricing_notes || obj.pricing_notes || 'N/A',
      aiExplanation: obj.aiExplanation || obj.ai_explanation || obj.explanation || 'No explanation provided.'
    };
  }

  backToForm(): void {
    this.step = 'form';
    this.cdr.markForCheck();
  }

  cancel(): void {
    this.dialogRef.close(false);
  }
}
