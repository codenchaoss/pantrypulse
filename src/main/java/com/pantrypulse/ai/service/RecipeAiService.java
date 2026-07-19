package com.pantrypulse.ai.service;

import org.springframework.stereotype.Service;

import com.pantrypulse.ai.client.AiClient;
import com.pantrypulse.ai.dto.RecipeRequestDto;
import com.pantrypulse.ai.dto.RecipeResponseDto;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class RecipeAiService {

    private final AiClient aiClient;

    public RecipeResponseDto recommendRecipe(RecipeRequestDto request) {

        return aiClient.recommendRecipe(request);

    }

}