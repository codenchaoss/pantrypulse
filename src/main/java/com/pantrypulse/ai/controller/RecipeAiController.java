package com.pantrypulse.ai.controller;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;

import com.pantrypulse.ai.dto.RecipeRequestDto;
import com.pantrypulse.ai.dto.RecipeResponseDto;
import com.pantrypulse.ai.service.RecipeAiService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
@ConditionalOnProperty(
	    name = "ai.enabled",
	    havingValue = "true"
	)
public class RecipeAiController {

    private final RecipeAiService recipeAiService;

    @PostMapping("/recipe")
    public RecipeResponseDto recommendRecipe(
            @RequestBody RecipeRequestDto request) {

        return recipeAiService.recommendRecipe(request);

    }

}