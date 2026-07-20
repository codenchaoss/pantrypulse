package com.pantrypulse.ai.service;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import com.pantrypulse.ai.client.AiClient;
import com.pantrypulse.ai.dto.MenuRequestDto;
import com.pantrypulse.ai.dto.MenuResponseDto;

@Service
@ConditionalOnProperty(
    name = "ai.enabled",
    havingValue = "true"
)
public class AiService {

    private final AiClient aiClient;

    public AiService(AiClient aiClient) {
        this.aiClient = aiClient;
    }

    public MenuResponseDto generateMenu(MenuRequestDto request) {
        return aiClient.generateMenu(request);
    }
}