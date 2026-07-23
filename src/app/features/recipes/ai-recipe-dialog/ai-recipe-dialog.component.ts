import { Component, OnInit, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { InventoryService } from '../../../services/inventory.service';
import { RecipeService } from '../../../core/services/recipe.service';
import { AiAssistantService } from '../../../core/services/ai-assistant.service';
import { Recipe, RecipeCategory } from '../../../core/models/recipe.model';

interface InventoryIngredient {
  id: number;
  ingredientName: string;
  category: string;
  quantity: number;
  unit: string;
  expiryDate?: string;
  daysToExpiry?: number;
  isExpiringSoon?: boolean;
  isExpired?: boolean;
}

@Component({
  selector: 'app-ai-recipe-dialog',
  templateUrl: './ai-recipe-dialog.component.html',
  styleUrls: ['./ai-recipe-dialog.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AiRecipeDialogComponent implements OnInit {
  title = 'AI Recipe Generator';
  
  step: 'select' | 'generate' | 'preview' = 'select';
  
  ingredients: InventoryIngredient[] = [];
  filteredIngredients: InventoryIngredient[] = [];
  selectedIngredients = new Set<string>();
  
  searchText = '';
  isLoadingIngredients = false;
  isLoadingRecipe = false;
  isSavingRecipe = false;
  errorMessage = '';

  generatedRecipe: any = null;
  editableRecipe: any = null;

  categories: { label: string; value: RecipeCategory }[] = [
    { label: 'Starter',     value: 'STARTER' },
    { label: 'Main Course', value: 'MAIN_COURSE' },
    { label: 'Dessert',     value: 'DESSERT' },
    { label: 'Beverage',    value: 'BEVERAGE' },
    { label: 'Snack',       value: 'SNACK' },
    { label: 'Salad',       value: 'SALAD' },
    { label: 'Soup',        value: 'SOUP' },
    { label: 'Side Dish',   value: 'SIDE_DISH' }
  ];

  constructor(
    private inventoryService: InventoryService,
    private recipeService: RecipeService,
    private aiAssistantService: AiAssistantService,
    private dialogRef: MatDialogRef<AiRecipeDialogComponent>,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadIngredients();
  }

  loadIngredients(): void {
    this.isLoadingIngredients = true;
    this.errorMessage = '';
    this.cdr.markForCheck();

    this.inventoryService.getIngredients().subscribe({
      next: (data) => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        this.ingredients = (data || []).map((item: any) => {
          let daysToExpiry: number | undefined;
          let isExpiringSoon = false;
          let isExpired = false;

          if (item.expiryDate) {
            const expiry = new Date(item.expiryDate);
            expiry.setHours(0, 0, 0, 0);
            const diffTime = expiry.getTime() - today.getTime();
            daysToExpiry = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (daysToExpiry < 0) {
              isExpired = true;
            } else if (daysToExpiry <= 7) {
              isExpiringSoon = true;
            }
          }

          return {
            id: item.id,
            ingredientName: item.ingredientName,
            category: item.category,
            quantity: item.quantity,
            unit: item.unit,
            expiryDate: item.expiryDate,
            daysToExpiry,
            isExpiringSoon,
            isExpired
          };
        });

        // Expiry Prioritization: Sort expired and expiring soon items to the top
        this.ingredients.sort((a, b) => {
          const scoreA = a.isExpired ? 2 : a.isExpiringSoon ? 1 : 0;
          const scoreB = b.isExpired ? 2 : b.isExpiringSoon ? 1 : 0;
          if (scoreA !== scoreB) {
            return scoreB - scoreA; // descending score
          }
          // Secondary sort by name
          return a.ingredientName.localeCompare(b.ingredientName);
        });

        this.applyFilter();
        this.isLoadingIngredients = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error loading inventory:', err);
        this.isLoadingIngredients = false;
        this.errorMessage = 'Failed to load ingredients from inventory.';
        this.cdr.markForCheck();
      }
    });
  }

  applyFilter(): void {
    if (!this.searchText.trim()) {
      this.filteredIngredients = [...this.ingredients];
    } else {
      const q = this.searchText.toLowerCase().trim();
      this.filteredIngredients = this.ingredients.filter(i => 
        i.ingredientName.toLowerCase().includes(q) || i.category.toLowerCase().includes(q)
      );
    }
    this.cdr.markForCheck();
  }

  toggleSelection(name: string): void {
    if (this.selectedIngredients.has(name)) {
      this.selectedIngredients.delete(name);
    } else {
      this.selectedIngredients.add(name);
    }
    this.cdr.markForCheck();
  }

  generateRecipe(): void {
    if (this.selectedIngredients.size === 0) return;

    this.step = 'generate';
    this.isLoadingRecipe = true;
    this.errorMessage = '';
    this.cdr.markForCheck();

    const selectedList = Array.from(this.selectedIngredients);

    this.aiAssistantService.generateRecipe(selectedList).subscribe({
      next: (res) => {
        this.isLoadingRecipe = false;
        try {
          this.generatedRecipe = this.parseAiResponse(res);
          // Prepopulate editable form fields
          this.editableRecipe = {
            ...this.generatedRecipe,
            ingredientsStr: Array.isArray(this.generatedRecipe.ingredients) 
              ? this.generatedRecipe.ingredients.join('\n') 
              : '',
            instructionsStr: Array.isArray(this.generatedRecipe.instructions) 
              ? this.generatedRecipe.instructions.join('\n') 
              : ''
          };
          this.step = 'preview';
        } catch (e: any) {
          console.error('Parsing error:', e);
          this.errorMessage = e.message || 'Failed to parse AI Recipe response.';
          this.step = 'select';
        }
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error generating AI Recipe:', err);
        this.isLoadingRecipe = false;
        this.step = 'select';
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
    if (!res) {
      throw new Error('Received an empty response from the AI Engine.');
    }

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

      // Strip markdown code wrap (e.g. ```json ... ```)
      if (trimmed.startsWith('```')) {
        const matches = trimmed.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
        if (matches && matches[1]) {
          cleaned = matches[1].trim();
        }
      }

      try {
        const json = JSON.parse(cleaned);
        if (json) return this.mapStructuredRecipe(json);
      } catch (e) {
        // Plain text parsing fallback
        return this.parsePlaintextRecipe(trimmed);
      }
    }

    if (rawData && typeof rawData === 'object') {
      return this.mapStructuredRecipe(rawData);
    }

    throw new Error('Format of AI response is unsupported.');
  }

  mapStructuredRecipe(obj: any): any {
    const recipeName = obj.recipeName || obj.title || obj.name || 'AI Special Dish';
    const description = obj.description || obj.summary || obj.reason || 'Generated by PantryPulse AI.';
    const preparationTime = Number(obj.preparationTime || obj.prepTime || obj.time || 20);
    const servings = Number(obj.servings || obj.serving || 2);
    const costPrice = Number(obj.costPrice || obj.cost || 0);
    const sellingPrice = Number(obj.sellingPrice || obj.price || 0);
    const calories = Number(obj.calories || obj.kcal || 350);
    const category = obj.category || 'MAIN_COURSE';
    
    let ingredientsList: string[] = [];
    if (Array.isArray(obj.ingredients)) {
      ingredientsList = obj.ingredients;
    } else if (typeof obj.ingredients === 'string') {
      ingredientsList = obj.ingredients.split('\n').map((s: string) => s.trim()).filter((s: string) => s.length > 0);
    }

    let instructionsList: string[] = [];
    if (Array.isArray(obj.instructions)) {
      instructionsList = obj.instructions;
    } else if (typeof obj.instructions === 'string') {
      instructionsList = obj.instructions.split('\n').map((s: string) => s.trim()).filter((s: string) => s.length > 0);
    }

    return {
      recipeName,
      description,
      preparationTime,
      servings,
      costPrice,
      sellingPrice,
      calories,
      category,
      ingredients: ingredientsList,
      instructions: instructionsList
    };
  }

  parsePlaintextRecipe(text: string): any {
    const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    let recipeName = 'AI Special Dish';
    if (lines.length > 0) {
      recipeName = lines[0].replace(/^[#*\s-]+|[#*\s:-]+$/g, '');
    }

    const description = lines.length > 1 ? lines.slice(1, Math.min(lines.length, 4)).join(' ') : 'AI Generated recipe suggestion.';
    
    return {
      recipeName: recipeName.substring(0, 50),
      description: description.substring(0, 200),
      preparationTime: 20,
      servings: 2,
      costPrice: 0,
      sellingPrice: 0,
      calories: 300,
      category: 'MAIN_COURSE',
      ingredients: Array.from(this.selectedIngredients),
      instructions: lines.slice(Math.min(lines.length, 4))
    };
  }

  saveRecipe(): void {
    if (!this.editableRecipe) return;

    this.isSavingRecipe = true;
    this.errorMessage = '';
    this.cdr.markForCheck();

    // Map editable form values back to recipe schema
    const recipeToSave: Recipe = {
      recipeName: this.editableRecipe.recipeName.trim(),
      category: this.editableRecipe.category,
      description: this.editableRecipe.description.trim(),
      preparationTime: Number(this.editableRecipe.preparationTime) || 15,
      servings: Number(this.editableRecipe.servings) || 2,
      costPrice: Number(this.editableRecipe.costPrice) || 0,
      sellingPrice: Number(this.editableRecipe.sellingPrice) || 0,
      calories: Number(this.editableRecipe.calories) || 300,
      available: true
    };

    // Split text fields by line breaks for storage in dialog state or logging
    const finalIngredients = this.editableRecipe.ingredientsStr
      .split('\n')
      .map((s: string) => s.trim())
      .filter((s: string) => s.length > 0);
    
    const finalInstructions = this.editableRecipe.instructionsStr
      .split('\n')
      .map((s: string) => s.trim())
      .filter((s: string) => s.length > 0);

    // Note: The base Recipe model saves fields. If database schemas expand, ingredients and instructions
    // are automatically recorded. We will submit the main recipe.
    this.recipeService.addRecipe(recipeToSave).subscribe({
      next: (saved) => {
        this.isSavingRecipe = false;
        this.dialogRef.close(true);
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error saving AI Recipe:', err);
        this.isSavingRecipe = false;
        if (err.status === 400 && err.error && err.error.message) {
          this.errorMessage = err.error.message;
        } else {
          this.errorMessage = 'Failed to save generated recipe to database.';
        }
        this.cdr.markForCheck();
      }
    });
  }

  cancel(): void {
    this.dialogRef.close(false);
  }

  backToSelect(): void {
    this.step = 'select';
    this.cdr.markForCheck();
  }
}
