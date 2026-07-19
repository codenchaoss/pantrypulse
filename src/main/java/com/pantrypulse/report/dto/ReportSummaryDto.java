package com.pantrypulse.report.dto;

import lombok.Data;

@Data
public class ReportSummaryDto {

    private long totalIngredients;

    private long totalRecipes;

    private long totalOrders;

    private long lowStockItems;

    private long expiredItems;

    private long expiringSoon;

}