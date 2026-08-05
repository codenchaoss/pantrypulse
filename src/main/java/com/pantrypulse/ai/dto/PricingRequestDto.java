package com.pantrypulse.ai.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PricingRequestDto {

    private String dish;

    @JsonProperty("ingredient_cost")
    private Double ingredientCost;
}