package com.pantrypulse.ai.dto;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryItemDto {

    private String ingredient;

    private String quantity;

    @JsonProperty("expiry_days")
    private Integer expiryDays;

}