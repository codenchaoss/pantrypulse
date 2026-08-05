package com.pantrypulse.ai.dto;

import lombok.Data;

@Data
public class RecommendedDishDto {

    private String dish;
    private Integer servings;
    private Double profit;
    private String priority;

}