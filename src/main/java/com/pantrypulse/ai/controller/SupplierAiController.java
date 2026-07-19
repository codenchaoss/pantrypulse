package com.pantrypulse.ai.controller;

import org.springframework.web.bind.annotation.*;

import com.pantrypulse.ai.dto.SupplierRequestDto;
import com.pantrypulse.ai.dto.SupplierResponseDto;
import com.pantrypulse.ai.service.SupplierAiService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor

public class SupplierAiController {

    private final SupplierAiService supplierAiService;

    @PostMapping("/supplier")
    public SupplierResponseDto generateSupplierMessage(
            @RequestBody SupplierRequestDto request) {

        return supplierAiService.generateSupplierMessage(request);

    }
}