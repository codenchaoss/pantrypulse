export interface SpecialMenuDto {
  dish: string;
  reason?: string;
  matched_inventory?: string[];
  matchedInventory?: string[];
  missing_ingredients?: string[];
  missingIngredients?: string[];
  estimated_profit?: string;
  estimatedProfit?: string;
  priority?: string;
  preparation_time?: number;
  preparationTime?: number;
  difficulty?: string;
  confidence?: number;
}

export interface MenuDataDto {
  special_menu?: SpecialMenuDto[];
  specialMenu?: SpecialMenuDto[];
}

export interface MenuResponseDto {
  success?: boolean;
  timestamp?: string;
  data?: MenuDataDto;
  message?: string;
}
