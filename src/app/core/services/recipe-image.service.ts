import { Injectable } from '@angular/core';

/**
 * RecipeImageService
 * ------------------
 * Stores and retrieves recipe images as Base64 strings in localStorage.
 * Key format: "pp_recipe_img_{recipeId}"
 *
 * No backend involved — pure client-side persistence.
 */
@Injectable({
  providedIn: 'root'
})
export class RecipeImageService {

  private readonly KEY_PREFIX = 'pp_recipe_img_';

  /** Persist a Base64 image string for a given recipe id. */
  saveImage(recipeId: number, base64: string): void {
    try {
      localStorage.setItem(this.KEY_PREFIX + recipeId, base64);
    } catch (e) {
      // localStorage full (5 MB quota) — fail gracefully
      console.warn('Could not save recipe image to localStorage:', e);
    }
  }

  /** Retrieve the stored Base64 string for a recipe id, or null if none. */
  getImage(recipeId: number): string | null {
    return localStorage.getItem(this.KEY_PREFIX + recipeId);
  }

  /** Remove a stored image (called on recipe delete). */
  removeImage(recipeId: number): void {
    localStorage.removeItem(this.KEY_PREFIX + recipeId);
  }

  /**
   * Validate a File before reading it.
   * Returns an error message string, or null if the file is valid.
   */
  validate(file: File): string | null {
    const allowed = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowed.includes(file.type)) {
      return 'Only JPG, JPEG, PNG, and WEBP images are allowed.';
    }
    const maxBytes = 2 * 1024 * 1024; // 2 MB
    if (file.size > maxBytes) {
      return `Image must be smaller than 2 MB. Selected file is ${(file.size / 1024 / 1024).toFixed(1)} MB.`;
    }
    return null;
  }

  /**
   * Read a File as a Base64 data URL.
   * Returns a Promise that resolves with the data URL string.
   */
  readAsBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload  = () => resolve(reader.result as string);
      reader.onerror = () => reject(new Error('Failed to read image file.'));
      reader.readAsDataURL(file);
    });
  }
}
