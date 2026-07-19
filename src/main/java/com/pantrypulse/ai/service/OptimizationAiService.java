package com.pantrypulse.ai.service;

import org.springframework.stereotype.Service;

import com.pantrypulse.ai.client.AiClient;
import com.pantrypulse.ai.dto.OptimizationRequestDto;
import com.pantrypulse.ai.dto.OptimizationResponseDto;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class OptimizationAiService {

    private final AiClient aiClient;

    public OptimizationResponseDto optimizeInventory(
            OptimizationRequestDto request) {

        return aiClient.optimizeInventory(request);

    }
}