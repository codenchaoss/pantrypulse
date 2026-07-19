package com.pantrypulse.recommendation.service;

import com.pantrypulse.inventory.entity.Inventory;
import com.pantrypulse.inventory.repository.InventoryRepository;
import com.pantrypulse.recommendation.dto.ExpiringIngredientDto;
import com.pantrypulse.recommendation.engine.ExpirationEngine;
import org.springframework.stereotype.Service;

import java.util.List;


@Service
public class ExpirationService {

    private final InventoryRepository inventoryRepository;
    private final ExpirationEngine expirationEngine;

    public ExpirationService(InventoryRepository inventoryRepository,
                             ExpirationEngine expirationEngine) {

        this.inventoryRepository = inventoryRepository;
        this.expirationEngine = expirationEngine;
    }

    public List<ExpiringIngredientDto> getExpiringIngredients() {
    	return inventoryRepository.findAll()
    	        .stream()
    	        .filter(expirationEngine::isExpiringSoon)
    	        .map(this::convert)
    	        .toList();

    }

    private ExpiringIngredientDto convert(Inventory inventory) {

        return ExpiringIngredientDto.builder()

                .inventoryId(inventory.getId())

                .ingredientName(inventory.getIngredientName())

                .quantity(inventory.getQuantity())

                .unit(inventory.getUnit())

                .expiryDate(inventory.getExpiryDate())

                .daysRemaining(
                        expirationEngine.calculateDaysRemaining(inventory)
                )

                .build();

    }

}