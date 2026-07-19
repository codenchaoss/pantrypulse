package com.pantrypulse.settings.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ApplicationPreferencesDto {

    private String language;

    private String currency;

    private String timeZone;

    private String dateFormat;
}