package com.pantrypulse.recommendation.controller;

import com.pantrypulse.recommendation.dto.ExpiringIngredientDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import com.pantrypulse.recommendation.service.ExpirationService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
@Tag(
        name="Expiration API",
        description="Detects ingredients approaching expiry."
)
@RestController
@RequestMapping("/api/expiration")
public class ExpirationController {

    private final ExpirationService expirationService;

    public ExpirationController(ExpirationService expirationService) {
        this.expirationService = expirationService;
    }

    @Operation(
    		summary="Get Expiring Ingredients",
    		description="Returns ingredients that will expire within the configured threshold."
    		)
    @GetMapping("/expiring")
    public List<ExpiringIngredientDto> getExpiringIngredients() {

        return expirationService.getExpiringIngredients();

    }

}