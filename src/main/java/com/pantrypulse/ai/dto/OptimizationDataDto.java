package com.pantrypulse.ai.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
public class OptimizationDataDto {

    @JsonProperty("recommended_dishes")
    private List<RecommendedDishDto> recommendedDishes;

    @JsonProperty("inventory_usage")
    private List<InventoryUsageDto> inventoryUsage;

    @JsonProperty("estimated_revenue")
    private Double estimatedRevenue;

    private String currency;

    @JsonProperty("waste_saved")
    private WasteSavedDto wasteSaved;

    @JsonProperty("remaining_inventory")
    private List<RemainingInventoryDto> remainingInventory;

    @JsonProperty("purchase_required")
    private Boolean purchaseRequired;

    @JsonProperty("purchase_items")
    private List<PurchaseItemDto> purchaseItems;

    private String reason;

    private String language;
}