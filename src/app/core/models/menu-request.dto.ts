export interface InventoryItemDto {
  ingredient: string;
  quantity: string;
  expiry_days?: number;
  expiryDays?: number;
}

export interface MenuRequestDto {
  inventory?: InventoryItemDto[];
  recipes?: string[];
}
