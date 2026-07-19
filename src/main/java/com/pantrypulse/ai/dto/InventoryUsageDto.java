package com.pantrypulse.ai.dto;

import lombok.Data;

@Data
public class InventoryUsageDto {

    private String ingredient;
    private Double used_quantity;
    private String unit;

}