package com.pantrypulse.ai.dto;

import lombok.Data;

@Data
public class RemainingInventoryDto {

    private String ingredient;
    private Double remaining_quantity;
    private String unit;

}