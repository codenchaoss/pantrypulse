package com.pantrypulse.settings.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SystemStatusDto {

    private String backend;

    private String aiService;

    private String database;
}