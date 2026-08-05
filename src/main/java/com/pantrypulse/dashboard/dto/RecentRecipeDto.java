package com.pantrypulse.dashboard.dto;

import lombok.Data;

@Data
public class RecentRecipeDto {

    private String recipeName;

    private String category;

    private String prepTime;

    private String status;

}