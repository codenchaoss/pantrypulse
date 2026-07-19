import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Recipe, RecipeCategory } from '../../../core/models/recipe.model';
import { RecipeService } from '../../../core/services/recipe.service';

@Component({
  selector: 'app-edit-recipe',
  templateUrl: './edit-recipe.component.html',
  styleUrls: ['./edit-recipe.component.css']
})
export class EditRecipeComponent implements OnInit {

  recipeId!: number;

  recipe: Recipe = {
    recipeName: '',
    category: '',
    description: '',
    preparationTime: null as any,
    servings: null as any,
    costPrice: null as any,
    sellingPrice: null as any,
    calories: null as any,
    available: true
  };

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

  isLoading: boolean = true;
  isSubmitting: boolean = false;
  loadError: string = '';
  successMessage: string = '';
  errorMessage: string = '';
  fieldErrors: { [key: string]: string } = {};

  // Image Upload properties
  imageFile: File | null = null;
  imagePreview: string | null = null;
  imageError: string = '';
  imageCleared: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private recipeService: RecipeService
  ) {}

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (!idParam || isNaN(Number(idParam))) {
      this.loadError = 'Invalid recipe ID in URL.';
      this.isLoading = false;
      return;
    }
    this.recipeId = Number(idParam);
    this.fetchRecipe();
  }

  fetchRecipe(): void {
    this.isLoading = true;
    this.loadError = '';

    this.recipeService.getRecipeById(this.recipeId).subscribe({
      next: (data: Recipe) => {
        // Deep copy to avoid mutating any shared reference
        this.recipe = { ...data };
        
        // Fetch image from localStorage
        this.imagePreview = localStorage.getItem('recipe_image_' + this.recipeId);
        this.imageCleared = false;
        
        this.isLoading = false;
      },
      error: (err) => {
        this.isLoading = false;
        if (err.status === 404) {
          this.loadError = `Recipe with ID ${this.recipeId} not found.`;
        } else if (err.status === 0) {
          this.loadError = 'Cannot connect to backend. Ensure Spring Boot is running on port 8080.';
        } else {
          this.loadError = `Failed to load recipe (HTTP ${err.status}).`;
        }
        console.error('Error fetching recipe:', err);
      }
    });
  }

  onFileSelected(event: any): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      return;
    }

    const file = input.files[0];
    this.imageError = '';

    // Validate type: JPG, JPEG, PNG, WEBP only
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      this.imageError = 'Only JPG, JPEG, PNG, and WEBP files are allowed.';
      this.imageFile = null;
      this.imagePreview = null;
      input.value = ''; // Reset input element
      return;
    }

    // Validate size: 2 MB limit
    const maxSizeBytes = 2 * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      this.imageError = 'Image size must be less than 2 MB.';
      this.imageFile = null;
      this.imagePreview = null;
      input.value = ''; // Reset input element
      return;
    }

    this.imageFile = file;
    this.imageCleared = false;

    // Convert file to Base64 string for immediate preview
    const reader = new FileReader();
    reader.onload = () => {
      this.imagePreview = reader.result as string;
    };
    reader.onerror = () => {
      this.imageError = 'Failed to read file.';
    };
    reader.readAsDataURL(file);
  }

  removeImage(): void {
    this.imageFile = null;
    this.imagePreview = null;
    this.imageError = '';
    this.imageCleared = true;
    // Reset file input in template
    const fileInput = document.getElementById('recipeImage') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }

  updateRecipe(form: NgForm): void {
    this.successMessage = '';
    this.errorMessage = '';
    this.fieldErrors = {};

    if (form.invalid) {
      form.form.markAllAsTouched();
      return;
    }

    // Log the outgoing payload for debugging
    console.log('PUT /api/recipes/' + this.recipeId, JSON.stringify(this.recipe, null, 2));

    this.isSubmitting = true;

    this.recipeService.updateRecipe(this.recipeId, this.recipe).subscribe({
      next: (updatedRecipe: Recipe) => {
        this.isSubmitting = false;

        // Save or remove image in localStorage
        if (this.imagePreview) {
          try {
            localStorage.setItem('recipe_image_' + this.recipeId, this.imagePreview);
          } catch (e) {
            console.error('Failed to save recipe image to localStorage:', e);
          }
        } else if (this.imageCleared) {
          localStorage.removeItem('recipe_image_' + this.recipeId);
        }

        this.successMessage = `Recipe "${updatedRecipe.recipeName}" updated successfully!`;
        console.log('Recipe updated:', updatedRecipe);
        setTimeout(() => {
          this.router.navigate(['/recipes']);
        }, 1500);
      },
      error: (error) => {
        this.isSubmitting = false;
        console.error('Error updating recipe:', error);

        if (error.status === 400 && error.error) {
          if (Array.isArray(error.error)) {
            error.error.forEach((err: any) => {
              this.fieldErrors[err.field] = err.defaultMessage;
            });
            this.errorMessage = 'Please fix the validation errors below.';
          } else if (error.error.errors) {
            error.error.errors.forEach((err: any) => {
              this.fieldErrors[err.field] = err.defaultMessage;
            });
            this.errorMessage = 'Please fix the validation errors below.';
          } else if (typeof error.error === 'string') {
            this.errorMessage = error.error;
          } else {
            this.errorMessage = 'Validation failed. Please check all fields.';
          }
        } else if (error.status === 404) {
          this.errorMessage = `Recipe with ID ${this.recipeId} no longer exists.`;
        } else if (error.status === 0) {
          this.errorMessage = 'Cannot connect to backend. Ensure Spring Boot is running on port 8080.';
        } else {
          this.errorMessage = `Server error (${error.status}): ${error.message}`;
        }
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/recipes']);
  }
}
