package com.pantrypulse.ai.service;

import org.springframework.stereotype.Service;

import com.pantrypulse.ai.client.AiClient;
import com.pantrypulse.ai.dto.MenuRequestDto;
import com.pantrypulse.ai.dto.MenuResponseDto;

@Service
public class AiService {

    private final AiClient aiClient;

    public AiService(AiClient aiClient) {
        this.aiClient = aiClient;
    }

    public MenuResponseDto generateMenu(MenuRequestDto request) {

        return aiClient.generateMenu(request);

    }

}