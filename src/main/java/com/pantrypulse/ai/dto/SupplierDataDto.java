package com.pantrypulse.ai.dto;

import lombok.Data;

@Data
public class SupplierDataDto {

    private String supplier_name;
    private String ingredient;
    private String message;
    private String language;
    private String subject;
    private String order_id;
    private String urgency;

}