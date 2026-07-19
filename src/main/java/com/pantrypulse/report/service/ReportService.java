package com.pantrypulse.report.service;

import java.time.LocalDate;

import org.springframework.stereotype.Service;

import com.pantrypulse.inventory.repository.InventoryRepository;
import com.pantrypulse.recipe.repository.RecipeRepository;
import com.pantrypulse.historicalorder.repository.HistoricalOrderRepository;
import com.pantrypulse.report.dto.ReportSummaryDto;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class ReportService {

    private final InventoryRepository inventoryRepository;

    private final RecipeRepository recipeRepository;

    private final HistoricalOrderRepository historicalOrderRepository;

    public ReportSummaryDto getSummary() {

        ReportSummaryDto dto = new ReportSummaryDto();

        dto.setTotalIngredients(inventoryRepository.count());

        dto.setTotalRecipes(recipeRepository.count());

        dto.setTotalOrders(historicalOrderRepository.count());

        dto.setLowStockItems(inventoryRepository.countLowStockItems());

        dto.setExpiredItems(inventoryRepository.countExpiredItems());

        dto.setExpiringSoon(
                inventoryRepository.countExpiringSoon(
                        LocalDate.now().plusDays(7)));

        return dto;
    }

}