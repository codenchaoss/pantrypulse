package com.pantrypulse.ai.controller;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import lombok.extern.slf4j.*;
import com.pantrypulse.ai.dto.ChatRequestDto;
import com.pantrypulse.ai.dto.ChatResponseDto;
import com.pantrypulse.ai.dto.MenuResponseDto;
import com.pantrypulse.ai.service.AiService;
import com.pantrypulse.recommendation.service.RecommendationService;
@Slf4j
@RestController
@RequestMapping("/api/ai")
@ConditionalOnProperty(
        name = "ai.enabled",
        havingValue = "true"
)
public class AiController {

    private final RecommendationService recommendationService;
    private final AiService aiService;

    public AiController(
            RecommendationService recommendationService,
            AiService aiService) {

        this.recommendationService = recommendationService;
        this.aiService = aiService;
    }

    @GetMapping("/menu")
    public MenuResponseDto generateMenu() {
        return recommendationService.generateMenu();
    }

    @PostMapping("/chat")
    public ChatResponseDto chat(@RequestBody ChatRequestDto request) {

        long start = System.currentTimeMillis();

        ChatResponseDto dto = aiService.chat(request);

        log.info("Chat controller completed in {} ms",
                System.currentTimeMillis() - start);

        return dto;
    }
}