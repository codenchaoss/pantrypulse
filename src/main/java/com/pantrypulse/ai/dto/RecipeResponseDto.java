package com.pantrypulse.ai.dto;

import lombok.Data;

@Data
public class RecipeResponseDto {

    private Boolean success;

    private String timestamp;

    private RecipeDataDto data;

}