package com.pantrypulse.ai.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class PricingDataDto {

    private String dish;

    @JsonProperty("ingredient_cost")
    private Double ingredientCost;

    @JsonProperty("recommended_price")
    private Double recommendedPrice;

    @JsonProperty("estimated_profit")
    private Double estimatedProfit;

    @JsonProperty("profit_margin")
    private Double profitMargin;

    @JsonProperty("pricing_strategy")
    private String pricingStrategy;

    @JsonProperty("market_position")
    private String marketPosition;

    @JsonProperty("price_confidence")
    private Double priceConfidence;
}