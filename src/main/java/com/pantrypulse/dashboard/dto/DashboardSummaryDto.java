package com.pantrypulse.dashboard.dto;

import java.util.List;

import lombok.Data;

@Data
public class DashboardSummaryDto {

    private long totalIngredients;

    private long totalRecipes;

    private long lowStockItems;

    private long expiringSoon;

    private long expiredItems;
    private List<RecentIngredientDto> recentIngredients;
    private List<RecentRecipeDto> recentRecipes;
    private List<ExpiryAlertDto> expiryAlerts;
}