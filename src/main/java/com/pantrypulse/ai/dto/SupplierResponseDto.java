package com.pantrypulse.ai.dto;

import lombok.Data;

@Data
public class SupplierResponseDto {

    private Boolean success;

    private String timestamp;

    private SupplierDataDto data;

    private String message;

}