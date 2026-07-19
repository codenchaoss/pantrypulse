package com.pantrypulse.ai.dto;

import lombok.Data;

@Data
public class PricingDataDto {

    private String dish;

    private Double ingredient_cost;

    private Double recommended_price;

    private Double estimated_profit;

    private Double profit_margin;

    private String pricing_strategy;

    private String market_position;

    private Double price_confidence;

}