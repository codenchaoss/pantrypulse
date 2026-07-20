package com.pantrypulse.ai.controller;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.pantrypulse.ai.dto.MenuResponseDto;
import com.pantrypulse.recommendation.service.RecommendationService;

@RestController
@RequestMapping("/api/ai")
@ConditionalOnProperty(
	    name = "ai.enabled",
	    havingValue = "true"
	)
public class AiController {

    private final RecommendationService recommendationService;

    public AiController(RecommendationService recommendationService) {
        this.recommendationService = recommendationService;
    }

    @GetMapping("/menu")
    public MenuResponseDto generateMenu() {
        return recommendationService.generateMenu();
    }
}