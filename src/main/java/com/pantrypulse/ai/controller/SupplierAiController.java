package com.pantrypulse.ai.controller;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;

import com.pantrypulse.ai.dto.SupplierRequestDto;
import com.pantrypulse.ai.dto.SupplierResponseDto;
import com.pantrypulse.ai.service.SupplierAiService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
@ConditionalOnProperty(
	    name = "ai.enabled",
	    havingValue = "true"
	)
public class SupplierAiController {

    private final SupplierAiService supplierAiService;

    @PostMapping("/supplier")
    public SupplierResponseDto generateSupplierMessage(
            @RequestBody SupplierRequestDto request) {

        return supplierAiService.generateSupplierMessage(request);

    }
}