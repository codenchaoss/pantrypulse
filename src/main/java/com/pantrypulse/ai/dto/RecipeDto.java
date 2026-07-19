package com.pantrypulse.ai.dto;

import lombok.Data;
import java.util.List;

@Data
public class RecipeDto {

    private String recipe_id;
    private String recipe_name;
    private String description;

    private List<String> matched_ingredients;
    private List<String> missing_ingredients;

    private Integer match_percentage;
    private Integer preparation_time_minutes;

    private String difficulty;

    private Integer estimated_calories;

    private String reason_for_recommendation;

    private Double confidence;

}