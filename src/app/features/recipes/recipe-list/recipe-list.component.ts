import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  OnDestroy,
  OnInit
} from '@angular/core';
import { Recipe, RecipeCategory } from '../../../core/models/recipe.model';
import { RecipeService } from '../../../core/services/recipe.service';
import { AiAssistantService } from '../../../core/services/ai-assistant.service';
import { MatDialog } from '@angular/material/dialog';
import { AiRecipeDialogComponent } from '../ai-recipe-dialog/ai-recipe-dialog.component';

@Component({
  selector: 'app-recipe-list',
  templateUrl: './recipe-list.component.html',
  styleUrls: ['./recipe-list.component.css'],
  // ── Fix #3: OnPush stops automatic re-renders on every browser event.
  // The component only re-renders when:
  //   a) An @Input() reference changes
  //   b) An Observable in the template emits (async pipe)
  //   c) We call cdr.markForCheck() explicitly
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class RecipeListComponent implements OnInit, OnDestroy {

  recipes: Recipe[] = [];
  filteredRecipes: Recipe[] = [];
  searchText = '';
  isLoading = true;
  errorMessage = '';

  selectedCategory = '';
  selectedAvailability = 'ALL';

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

  // Pagination state
  currentPage = 0;
  pageSize = 100;
  totalElements = 0;

  // ── Delete confirmation modal ──────────────────────────────────────────────
  showDeleteModal = false;
  recipeToDelete: Recipe | null = null;
  isDeleting = false;

  // ── AI Pricing suggestion modal ────────────────────────────────────────────
  showPricingModal = false;
  isPricingLoading = false;
  pricingError = '';
  pricingSuggestion: any = null;

  // ── Toast notification ─────────────────────────────────────────────────────
  toastMessage = '';
  toastType: 'success' | 'error' = 'success';
  private toastTimer: ReturnType<typeof setTimeout> | null = null;

  // ── Pre-computed display map — eliminates formatCategory() from template ──
  // Fix #1: Instead of calling a method in the template (evaluated every CD cycle),
  // we compute the display string once and store it in a Map keyed by recipe id.
  categoryDisplayMap = new Map<number, string>();

  constructor(
    private recipeService: RecipeService,
    private aiAssistantService: AiAssistantService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    // loadRecipes() is called exactly once here.
    // It will NOT be called again unless the user explicitly triggers
    // an Add / Edit / Delete operation.
    this.loadRecipes();
  }

  ngOnDestroy(): void {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
    }
  }

  private lastSearchText = '';

  // ── trackBy function — Fix #2 ──────────────────────────────────────────────
  // Angular uses this id to identify existing DOM nodes and reuse them
  // instead of destroying and recreating cards when the array changes.
  trackByRecipeId(index: number, recipe: Recipe): number | string {
    return recipe.id || recipe.recipeName || index;
  }

  loadRecipes(): void {
    this.isLoading = true;
    this.errorMessage = '';
    // Trigger render to show spinner (OnPush won't do it automatically)
    this.cdr.markForCheck();

    this.recipeService.getAllRecipes(this.currentPage, this.pageSize).subscribe({
      next: (response) => {
        this.recipes = response.content.map(recipe => ({
          ...recipe,
          imageUrl: recipe.id ? (localStorage.getItem('recipe_image_' + recipe.id) || undefined) : undefined
        }));
        this.filteredRecipes = this.recipes;
        this.totalElements = response.totalElements;
        this.isLoading = false;
        // Pre-compute category labels once per load — Fix #1
        this.buildCategoryDisplayMap(this.recipes);
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error loading recipes:', err);
        this.isLoading = false;
        if (err.status === 0) {
          this.errorMessage = 'Cannot connect to server. Ensure Spring Boot is running on port 8080.';
        } else {
          this.errorMessage = `Failed to load recipes (${err.status}).`;
        }
        this.cdr.markForCheck();
      }
    });
  }

  // ── Build lookup map for category labels ──────────────────────────────────
  private buildCategoryDisplayMap(recipes: Recipe[]): void {
    this.categoryDisplayMap.clear();
    recipes.forEach(r => {
      if (r.id !== undefined) {
        this.categoryDisplayMap.set(r.id, this.formatCategory(r.category));
      }
    });
  }

  searchRecipe(): void {
    const query = this.searchText.trim();
    if (query === this.lastSearchText) {
      return;
    }
    this.lastSearchText = query;

    this.selectedCategory = '';
    this.selectedAvailability = 'ALL';

    if (!query) {
      this.filteredRecipes = this.recipes;
      this.cdr.markForCheck();
    } else {
      this.isLoading = true;
      this.errorMessage = '';
      this.cdr.markForCheck();

      this.recipeService.searchRecipes(query).subscribe({
        next: (results) => {
          this.filteredRecipes = results.map(recipe => ({
            ...recipe,
            imageUrl: recipe.id ? (localStorage.getItem('recipe_image_' + recipe.id) || undefined) : undefined
          }));
          this.buildCategoryDisplayMap(this.filteredRecipes);
          this.isLoading = false;
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Error searching recipes:', err);
          this.isLoading = false;
          this.errorMessage = 'Failed to search recipes.';
          this.cdr.markForCheck();
        }
      });
    }
  }

  onCategoryChange(): void {
    this.searchText = '';
    this.selectedAvailability = 'ALL';
    this.lastSearchText = '';

    if (!this.selectedCategory) {
      this.loadRecipes();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.cdr.markForCheck();

    this.recipeService.getRecipesByCategory(this.selectedCategory).subscribe({
      next: (results) => {
        this.filteredRecipes = results.map(recipe => ({
          ...recipe,
          imageUrl: recipe.id ? (localStorage.getItem('recipe_image_' + recipe.id) || undefined) : undefined
        }));
        this.buildCategoryDisplayMap(this.filteredRecipes);
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error fetching recipes by category:', err);
        this.isLoading = false;
        this.errorMessage = 'Failed to load recipes for this category.';
        this.cdr.markForCheck();
      }
    });
  }

  onAvailabilityChange(): void {
    this.searchText = '';
    this.selectedCategory = '';
    this.lastSearchText = '';

    if (this.selectedAvailability === 'ALL') {
      this.loadRecipes();
      return;
    }

    const isAvailable = this.selectedAvailability === 'AVAILABLE';

    this.isLoading = true;
    this.errorMessage = '';
    this.cdr.markForCheck();

    this.recipeService.getAvailableRecipes(isAvailable).subscribe({
      next: (results) => {
        this.filteredRecipes = results.map(recipe => ({
          ...recipe,
          imageUrl: recipe.id ? (localStorage.getItem('recipe_image_' + recipe.id) || undefined) : undefined
        }));
        this.buildCategoryDisplayMap(this.filteredRecipes);
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error fetching available recipes:', err);
        this.isLoading = false;
        this.errorMessage = 'Failed to load recipes by availability.';
        this.cdr.markForCheck();
      }
    });
  }

  // ── Opens the custom confirmation modal ───────────────────────────────────
  requestDelete(recipe: Recipe): void {
    this.recipeToDelete = recipe;
    this.showDeleteModal = true;
    this.cdr.markForCheck();
  }

  // ── User clicked Cancel inside the modal ──────────────────────────────────
  cancelDelete(): void {
    this.showDeleteModal = false;
    this.recipeToDelete = null;
    this.isDeleting = false;
    this.cdr.markForCheck();
  }

  // ── User confirmed deletion ────────────────────────────────────────────────
  confirmDelete(): void {
    if (!this.recipeToDelete?.id) return;

    const id = this.recipeToDelete.id;
    const name = this.recipeToDelete.recipeName;
    this.isDeleting = true;
    this.cdr.markForCheck();

    this.recipeService.deleteRecipe(id).subscribe({
      next: () => {
        // Instant client-side removal — no full reload
        this.recipes = this.recipes.filter(r => r.id !== id);
        this.filteredRecipes = this.filteredRecipes.filter(r => r.id !== id);
        this.totalElements = Math.max(0, this.totalElements - 1);
        this.categoryDisplayMap.delete(id);

        // Delete image from localStorage
        localStorage.removeItem('recipe_image_' + id);

        this.showDeleteModal = false;
        this.recipeToDelete = null;
        this.isDeleting = false;

        this.showToast(`"${name}" deleted successfully.`, 'success');
        console.log(`Recipe ${id} deleted.`);
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.isDeleting = false;
        this.showDeleteModal = false;
        this.recipeToDelete = null;

        console.error('Error deleting recipe:', err);

        if (err.status === 404) {
          this.showToast('Recipe not found — it may have already been deleted.', 'error');
        } else if (err.status === 0) {
          this.showToast('Cannot connect to server. Ensure Spring Boot is running.', 'error');
        } else {
          this.showToast(`Failed to delete recipe (HTTP ${err.status}).`, 'error');
        }
        this.cdr.markForCheck();
      }
    });
  }

  // ── Auto-dismissing toast ─────────────────────────────────────────────────
  private showToast(message: string, type: 'success' | 'error'): void {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
    }
    this.toastMessage = message;
    this.toastType = type;
    this.cdr.markForCheck();

    this.toastTimer = setTimeout(() => {
      this.toastMessage = '';
      this.cdr.markForCheck();
    }, 3500);
  }

  dismissToast(): void {
    this.toastMessage = '';
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
      this.toastTimer = null;
    }
    this.cdr.markForCheck();
  }

  // ── Pure helper — only called programmatically, NOT in the template ───────
  private formatCategory(category: string): string {
    return category.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  // ── AI Pricing suggestion modal ────────────────────────────────────────────
  getAiPriceSuggestion(recipe: Recipe, event: Event): void {
    event.stopPropagation();
    this.showPricingModal = true;
    this.isPricingLoading = true;
    this.pricingError = '';
    this.pricingSuggestion = null;
    this.cdr.markForCheck();

    this.aiAssistantService.suggestPricing(recipe.recipeName, recipe.costPrice).subscribe({
      next: (res) => {
        this.isPricingLoading = false;
        if (res && res.success && res.data) {
          this.pricingSuggestion = res.data;
        } else {
          this.pricingError = res.message || 'Failed to generate price suggestion.';
        }
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.isPricingLoading = false;
        this.pricingError = 'AI Pricing service is currently unavailable. Ensure the AI profile is enabled on the backend.';
        console.error('AI Pricing error:', err);
        this.cdr.markForCheck();
      }
    });
  }

  closePricingModal(): void {
    this.showPricingModal = false;
    this.pricingSuggestion = null;
    this.pricingError = '';
    this.cdr.markForCheck();
  }

  openAiRecipeDialog(): void {
    const dialogRef = this.dialog.open(AiRecipeDialogComponent, {
      width: '750px',
      disableClose: true
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadRecipes();
      }
    });
  }

}