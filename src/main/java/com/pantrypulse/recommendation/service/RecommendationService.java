package com.pantrypulse.recommendation.service;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import com.pantrypulse.ai.dto.MenuRequestDto;
import com.pantrypulse.ai.dto.MenuResponseDto;
import com.pantrypulse.ai.mapper.AiRequestMapper;
import com.pantrypulse.ai.service.AiService;
import com.pantrypulse.historicalorder.repository.HistoricalOrderRepository;
import com.pantrypulse.recipe.entity.Recipe;
import com.pantrypulse.recipeingredient.entity.RecipeIngredient;
import com.pantrypulse.recipeingredient.repository.RecipeIngredientRepository;
import com.pantrypulse.recommendation.dto.AiRecommendationInputDto;
import com.pantrypulse.recommendation.dto.CandidateRecipeDto;
import com.pantrypulse.recommendation.dto.ExpiringIngredientDto;

@Service
@ConditionalOnProperty(
        name = "ai.enabled",
        havingValue = "true"
)
public class RecommendationService {

    private static final ZoneId APP_ZONE =
            ZoneId.of("Asia/Kolkata");

    private final ExpirationService expirationService;
    private final RecipeIngredientRepository recipeIngredientRepository;
    private final HistoricalOrderRepository historicalOrderRepository;
    private final AiRequestMapper aiRequestMapper;
    private final AiService aiService;

    public RecommendationService(
            ExpirationService expirationService,
            RecipeIngredientRepository recipeIngredientRepository,
            HistoricalOrderRepository historicalOrderRepository,
            AiRequestMapper aiRequestMapper,
            AiService aiService) {

        this.expirationService = expirationService;
        this.recipeIngredientRepository = recipeIngredientRepository;
        this.historicalOrderRepository = historicalOrderRepository;
        this.aiRequestMapper = aiRequestMapper;
        this.aiService = aiService;
    }

    public MenuResponseDto generateMenu() {

        AiRecommendationInputDto input = getRecommendationInput();

        if (input.getExpiringIngredients().isEmpty()) {

            return MenuResponseDto.builder()
                    .success(false)
                    .timestamp(LocalDateTime.now(APP_ZONE).toString())
                    .message(
                            "No expiring ingredients found. Add inventory with upcoming expiry dates."
                    )
                    .build();
        }

        MenuRequestDto request =
                aiRequestMapper.toMenuRequest(input);

        return aiService.generateMenu(request);
    }

    public AiRecommendationInputDto getRecommendationInput() {

        List<ExpiringIngredientDto> expiringIngredients =
                expirationService.getExpiringIngredients();

        List<CandidateRecipeDto> candidateRecipes =
                new ArrayList<>();

        Set<Long> processedRecipes =
                new HashSet<>();

        for (ExpiringIngredientDto ingredient : expiringIngredients) {

            List<RecipeIngredient> recipeIngredients =
                    recipeIngredientRepository.findByInventoryId(
                            ingredient.getInventoryId()
                    );

            for (RecipeIngredient recipeIngredient : recipeIngredients) {

                Recipe recipe =
                        recipeIngredient.getRecipe();

                if (processedRecipes.add(recipe.getId())) {

                    long popularity =
                            historicalOrderRepository
                                    .countByRecipeId(recipe.getId());

                    candidateRecipes.add(
                            CandidateRecipeDto.builder()
                                    .recipeId(recipe.getId())
                                    .recipeName(recipe.getRecipeName())
                                    .estimatedPopularity(popularity)
                                    .build()
                    );
                }
            }
        }

        candidateRecipes.sort(
                Comparator
                        .comparing(
                                CandidateRecipeDto::getEstimatedPopularity
                        )
                        .reversed()
        );

        return AiRecommendationInputDto.builder()
                .generatedAt(LocalDateTime.now(APP_ZONE))
                .expiringIngredients(expiringIngredients)
                .candidateRecipes(candidateRecipes)
                .build();
    }
}