export type RecipeCategory =
  | 'STARTER'
  | 'MAIN_COURSE'
  | 'DESSERT'
  | 'BEVERAGE'
  | 'SNACK'
  | 'SALAD'
  | 'SOUP'
  | 'SIDE_DISH';

export interface Recipe {
  id?: number;
  recipeName: string;
  category: RecipeCategory | string;
  description: string;
  preparationTime: number;
  servings: number;
  costPrice: number;
  sellingPrice: number;
  calories: number;
  available: boolean;
  imageUrl?: string;
}