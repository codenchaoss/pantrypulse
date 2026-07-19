package com.pantrypulse.ai.dto;

import lombok.Data;

import java.util.List;

@Data
public class OptimizationDataDto {

    private List<RecommendedDishDto> recommended_dishes;

    private List<InventoryUsageDto> inventory_usage;

    private Double estimated_revenue;

    private String currency;

    private WasteSavedDto waste_saved;

    private List<RemainingInventoryDto> remaining_inventory;

    private Boolean purchase_required;
    private List<PurchaseItemDto> purchase_items;

    private String reason;

    private String language;

}