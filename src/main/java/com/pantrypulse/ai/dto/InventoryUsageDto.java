package com.pantrypulse.ai.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class InventoryUsageDto {

    private String ingredient;

    @JsonProperty("used_quantity")
    private Double usedQuantity;

    private String unit;
}