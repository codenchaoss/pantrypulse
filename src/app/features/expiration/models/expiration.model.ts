export interface ExpiringIngredient {
  inventoryId: number;
  ingredientName: string;
  quantity: number;
  unit: string;
  expiryDate: string;
  daysRemaining: number;
  category?: string;
}