package com.pantrypulse.ai.service;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import com.pantrypulse.ai.client.AiClient;
import com.pantrypulse.ai.dto.PricingRequestDto;
import com.pantrypulse.ai.dto.PricingResponseDto;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@ConditionalOnProperty(
	    name = "ai.enabled",
	    havingValue = "true"
	)
public class PricingAiService {

    private final AiClient aiClient;

    public PricingResponseDto suggestPricing(PricingRequestDto request) {

        return aiClient.suggestPricing(request);

    }

}