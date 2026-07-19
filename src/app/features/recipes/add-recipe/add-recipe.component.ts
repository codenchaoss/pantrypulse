import { Component } from '@angular/core';
import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
import { Recipe, RecipeCategory } from '../../../core/models/recipe.model';
import { RecipeService } from '../../../core/services/recipe.service';

@Component({
  selector: 'app-add-recipe',
  templateUrl: './add-recipe.component.html',
  styleUrls: ['./add-recipe.component.css']
})
export class AddRecipeComponent {

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

  successMessage: string = '';
  errorMessage: string = '';
  fieldErrors: { [key: string]: string } = {};
  isSubmitting: boolean = false;

  // Image Upload properties
  imageFile: File | null = null;
  imagePreview: string | null = null;
  imageError: string = '';

  constructor(
    private recipeService: RecipeService,
    private router: Router
  ) {}

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
    // Reset file input in template
    const fileInput = document.getElementById('recipeImage') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }

  saveRecipe(form: NgForm): void {
    this.successMessage = '';
    this.errorMessage = '';
    this.fieldErrors = {};

    if (form.invalid) {
      form.form.markAllAsTouched();
      return;
    }

    // Log the payload for debugging
    console.log('Sending recipe payload:', JSON.stringify(this.recipe, null, 2));

    this.isSubmitting = true;

    this.recipeService.addRecipe(this.recipe).subscribe({
      next: (savedRecipe) => {
        this.isSubmitting = false;
        
        // Save base64 image in localStorage using recipe ID as key
        if (this.imagePreview && savedRecipe.id) {
          try {
            localStorage.setItem('recipe_image_' + savedRecipe.id, this.imagePreview);
          } catch (e) {
            console.error('Failed to save recipe image to localStorage:', e);
          }
        }

        this.successMessage = `Recipe "${savedRecipe.recipeName}" saved successfully!`;
        console.log('Recipe saved:', savedRecipe);
        setTimeout(() => {
          this.router.navigate(['/recipes']);
        }, 1500);
      },
      error: (error) => {
        this.isSubmitting = false;
        console.error('Error saving recipe:', error);

        if (error.status === 400 && error.error) {
          // Spring Boot @Valid returns field errors
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
        } else if (error.status === 0) {
          this.errorMessage = 'Cannot connect to backend. Ensure the Spring Boot server is running on port 8080.';
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