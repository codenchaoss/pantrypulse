package com.pantrypulse.recommendation.controller;

import com.pantrypulse.recommendation.dto.AiRecommendationInputDto;
import com.pantrypulse.recommendation.service.RecommendationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
@Tag(
	    name = "Recommendation API",
	    description = "Provides recommendation data for AI based on inventory and historical orders."
	)
@RestController
@RequestMapping("/api/recommendation")
@ConditionalOnProperty(
	    name = "ai.enabled",
	    havingValue = "true"
	)

public class RecommendationController {

    private final RecommendationService recommendationService;

    public RecommendationController(RecommendationService recommendationService) {
        this.recommendationService = recommendationService;
    }
    @Operation(
            summary = "Generate AI Recommendation Input",
            description = "Returns expiring ingredients and candidate recipes for the AI recommendation engine."
    )

    @GetMapping("/ai-input")
    public AiRecommendationInputDto getAiRecommendationInput() {
        return recommendationService.getRecommendationInput();
    }
}