package com.pantrypulse.recipeingredient.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RecipeIngredientDto {

    private Long id;

    @NotNull(message = "Recipe ID is required")
    private Long recipeId;

    @NotNull(message = "Inventory ID is required")
    private Long inventoryId;

    @NotNull(message = "Quantity is required")
    @Positive(message = "Quantity must be greater than 0")
    private Double quantity;

    @NotBlank(message = "Unit is required")
    private String unit;
}