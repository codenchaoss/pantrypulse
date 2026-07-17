package com.pantrypulse.inventory.dto;

import jakarta.validation.constraints.Future;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.*;

import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryDto {

    private Long id;

    @NotBlank(message = "Ingredient name is required")
    private String ingredientName;

    @NotNull(message = "Quantity is required")
    @Positive(message = "Quantity must be greater than zero")
    private Double quantity;

    @NotBlank(message = "Unit is required")
    private String unit;

    @NotBlank(message = "Category is required")
    private String category;

    @NotNull(message = "Expiry date is required")
    @Future(message = "Expiry date must be in the future")
    private LocalDate expiryDate;

    @NotNull(message = "Minimum stock is required")
    @Positive(message = "Minimum stock must be greater than zero")
    private Double minimumStock;

    @NotNull(message = "Availability status is required")
    private Boolean available;
}