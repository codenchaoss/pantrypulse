package com.pantrypulse.inventory.mapper;

import com.pantrypulse.inventory.dto.InventoryDto;
import com.pantrypulse.inventory.entity.Inventory;

public class InventoryMapper {

    private InventoryMapper() {
        // Utility class
    }

    public static InventoryDto toDto(Inventory inventory) {

        return InventoryDto.builder()
                .id(inventory.getId())
                .ingredientName(inventory.getIngredientName())
                .quantity(inventory.getQuantity())
                .unit(inventory.getUnit())
                .category(inventory.getCategory())
                .expiryDate(inventory.getExpiryDate())
                .minimumStock(inventory.getMinimumStock())
                .available(inventory.getAvailable())
                .build();
    }

    public static Inventory toEntity(InventoryDto dto) {

        return Inventory.builder()
                .id(dto.getId())
                .ingredientName(dto.getIngredientName())
                .quantity(dto.getQuantity())
                .unit(dto.getUnit())
                .category(dto.getCategory())
                .expiryDate(dto.getExpiryDate())
                .minimumStock(dto.getMinimumStock())
                .available(dto.getAvailable())
                .build();
    }
}