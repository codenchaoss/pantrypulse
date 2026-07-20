package com.pantrypulse.ai.controller;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;

import com.pantrypulse.ai.dto.PricingRequestDto;
import com.pantrypulse.ai.dto.PricingResponseDto;
import com.pantrypulse.ai.service.PricingAiService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
@ConditionalOnProperty(
	    name = "ai.enabled",
	    havingValue = "true"
	)
public class PricingAiController {

    private final PricingAiService pricingAiService;

    @PostMapping("/pricing")
    public PricingResponseDto suggestPricing(
            @RequestBody PricingRequestDto request) {

        return pricingAiService.suggestPricing(request);

    }

}