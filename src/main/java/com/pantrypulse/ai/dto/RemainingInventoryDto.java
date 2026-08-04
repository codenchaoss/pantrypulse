package com.pantrypulse.ai.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class RemainingInventoryDto {

    private String ingredient;

    @JsonProperty("remaining_quantity")
    private Double remainingQuantity;

    private String unit;
}