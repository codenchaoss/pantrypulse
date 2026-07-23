import { Recipe } from './recipe.model';

export interface HistoricalOrder {
  id?: number;
  recipeId: number;
  recipeName?: string;
  recipe?: Recipe;
  quantity: number;
  orderDate: string; // ISO date string (YYYY-MM-DD)
}
