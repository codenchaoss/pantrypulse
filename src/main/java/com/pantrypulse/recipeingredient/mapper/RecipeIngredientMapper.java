package com.pantrypulse.recipeingredient.mapper;

import com.pantrypulse.recipeingredient.dto.RecipeIngredientDto;
import com.pantrypulse.recipeingredient.entity.RecipeIngredient;

public class RecipeIngredientMapper {

    private RecipeIngredientMapper() {
        // Utility class
    }

    public static RecipeIngredientDto toDto(RecipeIngredient entity) {

        return RecipeIngredientDto.builder()
                .id(entity.getId())
                .recipeId(entity.getRecipe().getId())
                .inventoryId(entity.getInventory().getId())
                .quantity(entity.getQuantity())
                .unit(entity.getUnit())
                .build();
    }
}