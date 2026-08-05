package com.pantrypulse.ai.dto;

import lombok.Data;

@Data
public class OptimizationResponseDto {

    private Boolean success;

    private String timestamp;

    private OptimizationDataDto data;

    private String message;

}