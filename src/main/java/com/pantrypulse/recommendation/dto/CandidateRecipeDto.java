package com.pantrypulse.recommendation.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CandidateRecipeDto {

    private Long recipeId;

    private String recipeName;

    private Long estimatedPopularity;

}