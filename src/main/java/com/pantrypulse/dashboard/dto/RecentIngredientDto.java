package com.pantrypulse.dashboard.dto;

import lombok.Data;

@Data
public class RecentIngredientDto {

    private String ingredient;

    private Double quantity;

    private String expiry;

    private String status;
}