package com.pantrypulse.ai.dto;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MenuDataDto {

    @JsonProperty("special_menu")
    private List<SpecialMenuDto> specialMenu;

}