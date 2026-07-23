import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Recipe } from '../../../core/models/recipe.model';
import { RecipeService } from '../../../core/services/recipe.service';
import { AiAssistantService } from '../../../core/services/ai-assistant.service';

@Component({
  selector: 'app-recipe-details',
  templateUrl: './recipe-details.component.html',
  styleUrls: ['./recipe-details.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class RecipeDetailsComponent implements OnInit {

  recipeId!: number;
  recipe: Recipe | null = null;
  imagePreview: string | null = null;
  
  isLoading = true;
  errorMessage = '';
  
  showDeleteModal = false;
  isDeleting = false;

  // ── AI Pricing suggestion modal ────────────────────────────────────────────
  showPricingModal = false;
  isPricingLoading = false;
  pricingError = '';
  pricingSuggestion: any = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private recipeService: RecipeService,
    private aiAssistantService: AiAssistantService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (!idParam || isNaN(Number(idParam))) {
      this.errorMessage = 'Invalid Recipe ID.';
      this.isLoading = false;
      return;
    }
    this.recipeId = Number(idParam);
    this.fetchRecipe();
  }

  fetchRecipe(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.cdr.markForCheck();

    this.recipeService.getRecipeById(this.recipeId).subscribe({
      next: (data: Recipe) => {
        this.recipe = data;
        this.imagePreview = localStorage.getItem('recipe_image_' + this.recipeId);
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error loading recipe details:', err);
        this.isLoading = false;
        if (err.status === 404) {
          this.errorMessage = 'Recipe not found.';
        } else if (err.status === 0) {
          this.errorMessage = 'Cannot connect to backend. Ensure server is running.';
        } else {
          this.errorMessage = `Failed to load recipe details (${err.status}).`;
        }
        this.cdr.markForCheck();
      }
    });
  }

  formatCategory(category: string | undefined): string {
    if (!category) return '';
    return category.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  goBack(): void {
    this.router.navigate(['/recipes']);
  }

  editRecipe(): void {
    this.router.navigate(['/recipes/edit', this.recipeId]);
  }

  requestDelete(): void {
    this.showDeleteModal = true;
    this.cdr.markForCheck();
  }

  cancelDelete(): void {
    this.showDeleteModal = false;
    this.cdr.markForCheck();
  }

  confirmDelete(): void {
    this.isDeleting = true;
    this.cdr.markForCheck();

    this.recipeService.deleteRecipe(this.recipeId).subscribe({
      next: () => {
        // Clean local storage image
        localStorage.removeItem('recipe_image_' + this.recipeId);
        this.isDeleting = false;
        this.showDeleteModal = false;
        this.router.navigate(['/recipes']);
      },
      error: (err) => {
        console.error('Failed to delete recipe:', err);
        this.isDeleting = false;
        this.showDeleteModal = false;
        this.errorMessage = 'Failed to delete recipe. Please try again.';
        this.cdr.markForCheck();
      }
    });
  }

  // ── AI Pricing suggestion modal ────────────────────────────────────────────
  getAiPriceSuggestion(): void {
    if (!this.recipe) return;
    this.showPricingModal = true;
    this.isPricingLoading = true;
    this.pricingError = '';
    this.pricingSuggestion = null;
    this.cdr.markForCheck();

    this.aiAssistantService.suggestPricing(this.recipe.recipeName, this.recipe.costPrice).subscribe({
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
}
