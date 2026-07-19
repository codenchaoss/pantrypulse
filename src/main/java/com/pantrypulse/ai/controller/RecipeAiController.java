package com.pantrypulse.ai.controller;

import org.springframework.web.bind.annotation.*;

import com.pantrypulse.ai.dto.RecipeRequestDto;
import com.pantrypulse.ai.dto.RecipeResponseDto;
import com.pantrypulse.ai.service.RecipeAiService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor

public class RecipeAiController {

    private final RecipeAiService recipeAiService;

    @PostMapping("/recipe")
    public RecipeResponseDto recommendRecipe(
            @RequestBody RecipeRequestDto request) {

        return recipeAiService.recommendRecipe(request);

    }

}