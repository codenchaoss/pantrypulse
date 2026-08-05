package com.pantrypulse.ai.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SupplierRequestDto {

    @JsonProperty("supplier_name")
    private String supplierName;

    private String ingredient;

    @JsonProperty("required_quantity")
    private String requiredQuantity;

    @JsonProperty("required_date")
    private String requiredDate;

    private List<String> ingredients;

    @JsonProperty("restaurant_name")
    private String restaurantName;

    @JsonProperty("contact_person")
    private String contactPerson;

    @JsonProperty("supplier_email")
    private String supplierEmail;

    @JsonProperty("supplier_phone")
    private String supplierPhone;

    @JsonProperty("urgency_level")
    private String urgencyLevel;

    @JsonProperty("language_preference")
    private String languagePreference;
}