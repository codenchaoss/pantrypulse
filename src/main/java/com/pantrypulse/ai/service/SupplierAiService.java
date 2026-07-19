package com.pantrypulse.ai.service;

import org.springframework.stereotype.Service;

import com.pantrypulse.ai.client.AiClient;
import com.pantrypulse.ai.dto.SupplierRequestDto;
import com.pantrypulse.ai.dto.SupplierResponseDto;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class SupplierAiService {

    private final AiClient aiClient;

    public SupplierResponseDto generateSupplierMessage(
            SupplierRequestDto request) {

        return aiClient.generateSupplierMessage(request);

    }
}