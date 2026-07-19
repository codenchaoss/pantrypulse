	package com.pantrypulse.recommendation.dto;
	import lombok.*;
	@Getter
	@Setter
	@NoArgsConstructor
	@AllArgsConstructor
	@Builder
	public class HistoricalRecipeStatsDto {

	    private String recipeName;

	    private Integer totalOrders;

	}