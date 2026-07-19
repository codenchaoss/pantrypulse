package com.pantrypulse.ai.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SupplierRequestDto {

    private String supplier_name;
    private String ingredient;
    private String required_quantity;
    private String required_date;

    private List<String> ingredients;

    private String restaurant_name;
    private String contact_person;

    private String supplier_email;
    private String supplier_phone;

    private String urgency_level;
    private String language_preference;

}