package com.pantrypulse.historicalorder.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class HistoricalOrderDto {

    private Long id;

    @NotNull(message = "Recipe ID is required")
    private Long recipeId;

    private String recipeName;

    @NotNull(message = "Quantity is required")
    @Min(value = 1, message = "Quantity must be at least 1")
    private Integer quantity;

    @NotNull(message = "Order date is required")
    private LocalDate orderDate;
}