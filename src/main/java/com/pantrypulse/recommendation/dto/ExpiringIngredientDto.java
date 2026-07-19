package com.pantrypulse.recommendation.dto;

import lombok.*;

import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ExpiringIngredientDto {

    private Long inventoryId;

    private String ingredientName;

    private Double quantity;

    private String unit;

    private LocalDate expiryDate;

    private long daysRemaining;
}