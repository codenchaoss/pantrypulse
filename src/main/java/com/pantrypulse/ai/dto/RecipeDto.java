package com.pantrypulse.ai.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
public class RecipeDto {

    @JsonProperty("recipe_id")
    private String recipeId;

    @JsonProperty("recipe_name")
    private String recipeName;

    private String description;

    @JsonProperty("matched_ingredients")
    private List<String> matchedIngredients;

    @JsonProperty("missing_ingredients")
    private List<String> missingIngredients;

    @JsonProperty("match_percentage")
    private Integer matchPercentage;

    @JsonProperty("preparation_time_minutes")
    private Integer preparationTimeMinutes;

    private String difficulty;

    @JsonProperty("estimated_calories")
    private Integer estimatedCalories;

    @JsonProperty("reason_for_recommendation")
    private String reasonForRecommendation;

    private Double confidence;
}