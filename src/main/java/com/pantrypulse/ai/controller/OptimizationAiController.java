package com.pantrypulse.ai.controller;

import org.springframework.web.bind.annotation.*;

import com.pantrypulse.ai.dto.OptimizationRequestDto;
import com.pantrypulse.ai.dto.OptimizationResponseDto;
import com.pantrypulse.ai.service.OptimizationAiService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
public class OptimizationAiController {

    private final OptimizationAiService optimizationAiService;

    @PostMapping("/optimization")
    public OptimizationResponseDto optimizeInventory(
            @RequestBody OptimizationRequestDto request) {

        return optimizationAiService.optimizeInventory(request);

    }
}