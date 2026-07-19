export interface RecipeIngredientMapping {
  id: number;
  recipeId: number;
  recipeName: string;
  inventoryId: number;
  ingredientName: string;
  quantity: number;
  unit: string;
}
