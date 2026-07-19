import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { RecipeIngredientMapping } from '../core/models/recipe-ingredient.model';

@Injectable({
  providedIn: 'root'
})
export class RecipeIngredientsService {
  
  private readonly STORAGE_KEY = 'pantrypulse_recipe_ingredients';

  constructor() {
    this.initMockDataIfNeeded();
  }

  private initMockDataIfNeeded(): void {
    if (!localStorage.getItem(this.STORAGE_KEY)) {
      const mockData: RecipeIngredientMapping[] = [
        {
          id: 101,
          recipeId: 1,
          recipeName: 'Paneer Butter Masala',
          inventoryId: 10,
          ingredientName: 'Cottage Cheese (Paneer)',
          quantity: 250,
          unit: 'g'
        },
        {
          id: 102,
          recipeId: 1,
          recipeName: 'Paneer Butter Masala',
          inventoryId: 11,
          ingredientName: 'Butter',
          quantity: 50,
          unit: 'g'
        }
      ];
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(mockData));
    }
  }

  getMappings(): Observable<RecipeIngredientMapping[]> {
    const dataStr = localStorage.getItem(this.STORAGE_KEY);
    const list: RecipeIngredientMapping[] = dataStr ? JSON.parse(dataStr) : [];
    return of(list);
  }

  addMapping(mapping: Omit<RecipeIngredientMapping, 'id'>): Observable<RecipeIngredientMapping> {
    const dataStr = localStorage.getItem(this.STORAGE_KEY);
    const list: RecipeIngredientMapping[] = dataStr ? JSON.parse(dataStr) : [];
    
    const newId = list.length > 0 ? Math.max(...list.map(m => m.id)) + 1 : 1;
    const newMapping: RecipeIngredientMapping = {
      ...mapping,
      id: newId
    };

    list.push(newMapping);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(list));
    return of(newMapping);
  }

  updateMapping(id: number, updatedFields: Partial<RecipeIngredientMapping>): Observable<RecipeIngredientMapping> {
    const dataStr = localStorage.getItem(this.STORAGE_KEY);
    const list: RecipeIngredientMapping[] = dataStr ? JSON.parse(dataStr) : [];
    
    const index = list.findIndex(m => m.id === id);
    if (index === -1) {
      throw new Error(`Mapping with id ${id} not found.`);
    }

    const updatedMapping = {
      ...list[index],
      ...updatedFields
    };

    list[index] = updatedMapping;
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(list));
    return of(updatedMapping);
  }

  deleteMapping(id: number): Observable<boolean> {
    const dataStr = localStorage.getItem(this.STORAGE_KEY);
    const list: RecipeIngredientMapping[] = dataStr ? JSON.parse(dataStr) : [];
    
    const filtered = list.filter(m => m.id !== id);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filtered));
    return of(true);
  }
}
