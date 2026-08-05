package com.pantrypulse.ai.dto;

import lombok.Data;

@Data
public class PricingResponseDto {

    private Boolean success;

    private String timestamp;

    private PricingDataDto data;

    private String message;

}