package com.pantrypulse.settings.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AiPreferencesDto {

    private Boolean enableAiMenuPlanner;

    private Boolean enableAiAssistant;

    private String defaultCuisine;

    private String menuGenerationFrequency;
}