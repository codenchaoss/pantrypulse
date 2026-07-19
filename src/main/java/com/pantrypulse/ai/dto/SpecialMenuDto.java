package com.pantrypulse.ai.dto;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SpecialMenuDto {

    private String dish;

    private String reason;

    @JsonProperty("matched_inventory")
    private List<String> matchedInventory;

    @JsonProperty("missing_ingredients")
    private List<String> missingIngredients;

    @JsonProperty("estimated_profit")
    private String estimatedProfit;

    private String priority;

    @JsonProperty("preparation_time")
    private Integer preparationTime;

    private String difficulty;

    private Double confidence;

}