package com.pantrypulse.ai.controller;

import org.springframework.web.bind.annotation.*;

import com.pantrypulse.ai.dto.PricingRequestDto;
import com.pantrypulse.ai.dto.PricingResponseDto;
import com.pantrypulse.ai.service.PricingAiService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
public class PricingAiController {

    private final PricingAiService pricingAiService;

    @PostMapping("/pricing")
    public PricingResponseDto suggestPricing(
            @RequestBody PricingRequestDto request) {

        return pricingAiService.suggestPricing(request);

    }

}