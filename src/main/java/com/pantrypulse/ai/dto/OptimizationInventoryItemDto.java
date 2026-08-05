package com.pantrypulse.ai.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
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

    @JsonProperty("expiry_days")
    private Integer expiryDays;
}