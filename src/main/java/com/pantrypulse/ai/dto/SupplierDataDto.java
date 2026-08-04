package com.pantrypulse.ai.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class SupplierDataDto {

    @JsonProperty("supplier_name")
    private String supplierName;

    private String ingredient;
    private String message;
    private String language;
    private String subject;

    @JsonProperty("order_id")
    private String orderId;

    private String urgency;
}