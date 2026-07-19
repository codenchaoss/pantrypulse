package com.pantrypulse.ai.mapper;

import java.util.List;

import org.springframework.stereotype.Component;

import com.pantrypulse.ai.dto.InventoryItemDto;
import com.pantrypulse.ai.dto.MenuRequestDto;
import com.pantrypulse.recommendation.dto.AiRecommendationInputDto;

@Component
public class AiRequestMapper {

    public MenuRequestDto toMenuRequest(AiRecommendationInputDto input) {

        List<InventoryItemDto> inventory =
                input.getExpiringIngredients()
                        .stream()
                        .map(item -> InventoryItemDto.builder()
                                .ingredient(item.getIngredientName())
                                .quantity(item.getQuantity() + " " + item.getUnit())
                                .expiryDays((int) item.getDaysRemaining())
                                .build())
                        .toList();

        List<String> recipes =
                input.getCandidateRecipes()
                        .stream()
                        .map(recipe -> recipe.getRecipeName())
                        .toList();

        return MenuRequestDto.builder()
                .inventory(inventory)
                .recipes(recipes)
                .build();
    }
}