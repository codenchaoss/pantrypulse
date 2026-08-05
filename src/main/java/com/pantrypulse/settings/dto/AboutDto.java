package com.pantrypulse.settings.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AboutDto {

    private String application;

    private String systemVersion;

    private String frontendVersion;

    private String backendVersion;

    private String angularVersion;

    private String springBootVersion;

    private String database;
}