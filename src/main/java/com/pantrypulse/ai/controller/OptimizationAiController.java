package com.pantrypulse.ai.controller;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;

import com.pantrypulse.ai.dto.OptimizationRequestDto;
import com.pantrypulse.ai.dto.OptimizationResponseDto;
import com.pantrypulse.ai.service.OptimizationAiService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
@ConditionalOnProperty(
	    name = "ai.enabled",
	    havingValue = "true"
	)
public class OptimizationAiController {

    private final OptimizationAiService optimizationAiService;

    @PostMapping("/optimization")
    public OptimizationResponseDto optimizeInventory(
            @RequestBody OptimizationRequestDto request) {

        return optimizationAiService.optimizeInventory(request);

    }
}