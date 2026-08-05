package com.pantrypulse.recommendation.service;

import com.pantrypulse.inventory.entity.Inventory;
import com.pantrypulse.inventory.repository.InventoryRepository;
import com.pantrypulse.recommendation.dto.ExpiringIngredientDto;
import com.pantrypulse.recommendation.engine.ExpirationEngine;
import org.springframework.stereotype.Service;
import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.authentication.service.AuthenticatedUserService;

import java.util.List;


@Service
public class ExpirationService {

    private final InventoryRepository inventoryRepository;
    private final ExpirationEngine expirationEngine;
    private final AuthenticatedUserService authenticatedUserService;

    public ExpirationService(
            InventoryRepository inventoryRepository,
            ExpirationEngine expirationEngine,
            AuthenticatedUserService authenticatedUserService) {

        this.inventoryRepository = inventoryRepository;
        this.expirationEngine = expirationEngine;
        this.authenticatedUserService = authenticatedUserService;
    }

    public List<ExpiringIngredientDto> getExpiringIngredients() {

        User currentUser = authenticatedUserService.getCurrentUser();

        return inventoryRepository.findByOwner(currentUser)
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