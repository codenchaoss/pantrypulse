package com.pantrypulse.recipe.dto;

import com.pantrypulse.recipe.enums.RecipeCategory;
import jakarta.validation.constraints.*;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RecipeDto {

    private Long id;

    @NotBlank(message = "Recipe name is required")
    private String recipeName;

    @NotNull(message = "Category is required")
    private RecipeCategory category;

    @Size(max = 500, message = "Description cannot exceed 500 characters")
    private String description;

    @NotNull(message = "Preparation time is required")
    @Positive(message = "Preparation time must be greater than 0")
    private Integer preparationTime;

    @NotNull(message = "Servings are required")
    @Positive(message = "Servings must be greater than 0")
    private Integer servings;

    @NotNull(message = "Cost price is required")
    @Positive(message = "Cost price must be greater than 0")
    private Double costPrice;

    @NotNull(message = "Selling price is required")
    @Positive(message = "Selling price must be greater than 0")
    private Double sellingPrice;

    @Positive(message = "Calories must be greater than 0")
    private Integer calories;

    @NotNull(message = "Availability is required")
    private Boolean available;
}