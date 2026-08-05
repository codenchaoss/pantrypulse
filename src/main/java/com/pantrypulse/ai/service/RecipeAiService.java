package com.pantrypulse.ai.service;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import com.pantrypulse.ai.client.AiClient;
import com.pantrypulse.ai.dto.RecipeRequestDto;
import com.pantrypulse.ai.dto.RecipeResponseDto;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@ConditionalOnProperty(
	    name = "ai.enabled",
	    havingValue = "true"
	)	
public class RecipeAiService {

    private final AiClient aiClient;

    public RecipeResponseDto recommendRecipe(RecipeRequestDto request) {

        return aiClient.recommendRecipe(request);

    }

}