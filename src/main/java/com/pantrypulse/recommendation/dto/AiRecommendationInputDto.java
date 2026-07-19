package com.pantrypulse.recommendation.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiRecommendationInputDto {

    private LocalDateTime generatedAt;

    private List<ExpiringIngredientDto> expiringIngredients;

    private List<CandidateRecipeDto> candidateRecipes;

}