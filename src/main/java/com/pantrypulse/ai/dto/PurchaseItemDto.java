package com.pantrypulse.ai.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class PurchaseItemDto {

    private String ingredient;

    @JsonProperty("required_quantity")
    private String requiredQuantity;
}