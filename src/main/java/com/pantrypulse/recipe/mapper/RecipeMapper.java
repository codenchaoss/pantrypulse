package com.pantrypulse.recipe.mapper;

import com.pantrypulse.recipe.dto.RecipeDto;
import com.pantrypulse.recipe.entity.Recipe;

public class RecipeMapper {

    public static RecipeDto toDto(Recipe recipe) {

        return RecipeDto.builder()
                .id(recipe.getId())
                .recipeName(recipe.getRecipeName())
                .category(recipe.getCategory())
                .description(recipe.getDescription())
                .preparationTime(recipe.getPreparationTime())
                .servings(recipe.getServings())
                .costPrice(recipe.getCostPrice())
                .sellingPrice(recipe.getSellingPrice())
                .calories(recipe.getCalories())
                .available(recipe.getAvailable())
                .build();
    }

    public static Recipe toEntity(RecipeDto dto) {

        return Recipe.builder()
                .id(dto.getId())
                .recipeName(dto.getRecipeName())
                .category(dto.getCategory())
                .description(dto.getDescription())
                .preparationTime(dto.getPreparationTime())
                .servings(dto.getServings())
                .costPrice(dto.getCostPrice())
                .sellingPrice(dto.getSellingPrice())
                .calories(dto.getCalories())
                .available(dto.getAvailable())
                .build();
    }
}