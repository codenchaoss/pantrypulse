package com.pantrypulse.ai.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class OptimizationInventoryItemDto {

    private String ingredient;
    private Integer quantity;
    private String unit;
    private Integer expiry_days;

}