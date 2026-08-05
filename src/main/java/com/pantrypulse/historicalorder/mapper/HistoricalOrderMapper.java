package com.pantrypulse.historicalorder.mapper;

import com.pantrypulse.historicalorder.dto.HistoricalOrderDto;
import com.pantrypulse.historicalorder.entity.HistoricalOrder;

public class HistoricalOrderMapper {

    private HistoricalOrderMapper() {
        // Utility class
    }

    public static HistoricalOrderDto toDto(HistoricalOrder order) {

        return HistoricalOrderDto.builder()
                .id(order.getId())
                .recipeId(order.getRecipe().getId())
                .recipeName(order.getRecipe().getRecipeName())
                .quantity(order.getQuantity())
                .orderDate(order.getOrderDate())
                .build();
    }
}