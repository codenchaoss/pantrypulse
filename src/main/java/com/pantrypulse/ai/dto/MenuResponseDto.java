package com.pantrypulse.ai.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MenuResponseDto {

    private Boolean success;

    private String timestamp;

    private MenuDataDto data;

    private String message;

}