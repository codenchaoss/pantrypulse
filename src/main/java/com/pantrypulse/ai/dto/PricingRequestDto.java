package com.pantrypulse.ai.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PricingRequestDto {

    private String dish;
    private Double ingredient_cost;

}