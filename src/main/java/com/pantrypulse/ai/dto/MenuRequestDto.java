package com.pantrypulse.ai.dto;

import lombok.*;

import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MenuRequestDto {

    private List<InventoryItemDto> inventory;

    private List<String> recipes;

}