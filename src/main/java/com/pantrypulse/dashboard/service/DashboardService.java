package com.pantrypulse.dashboard.service;

import org.springframework.stereotype.Service;
import java.time.LocalDate;
import java.util.List;
import com.pantrypulse.dashboard.dto.RecentRecipeDto;

import com.pantrypulse.dashboard.dto.RecentIngredientDto;
import com.pantrypulse.dashboard.dto.ExpiryAlertDto;
import com.pantrypulse.dashboard.dto.DashboardSummaryDto;
import com.pantrypulse.inventory.repository.InventoryRepository;
import com.pantrypulse.recipe.repository.RecipeRepository;

@Service
public class DashboardService {

	private final InventoryRepository inventoryRepository;

	private final RecipeRepository recipeRepository;

	public DashboardService(InventoryRepository inventoryRepository, RecipeRepository recipeRepository) {

		this.inventoryRepository = inventoryRepository;
		this.recipeRepository = recipeRepository;
	}

	public DashboardSummaryDto getSummary() {

		DashboardSummaryDto dto = new DashboardSummaryDto();

		dto.setTotalIngredients(inventoryRepository.count());

		dto.setTotalRecipes(recipeRepository.count());

		dto.setLowStockItems(inventoryRepository.countLowStockItems());

		dto.setExpiringSoon(inventoryRepository.countExpiringSoon(LocalDate.now().plusDays(7)));

		dto.setExpiredItems(inventoryRepository.countExpiredItems());
		List<RecentIngredientDto> recentIngredients = inventoryRepository.findTop5ByOrderByIdDesc().stream()
				.map(item -> {

					RecentIngredientDto r = new RecentIngredientDto();

					r.setIngredient(item.getIngredientName());

					r.setQuantity(item.getQuantity());

					r.setExpiry(item.getExpiryDate().toString());

					if (item.getQuantity() <= item.getMinimumStock()) {
						r.setStatus("Low Stock");
					} else {
						r.setStatus("Available");
					}

					return r;

				}).toList();

		dto.setRecentIngredients(recentIngredients);
		List<RecentRecipeDto> recentRecipes = recipeRepository.findTop5ByOrderByIdDesc().stream().map(recipe -> {

			RecentRecipeDto r = new RecentRecipeDto();

			r.setRecipeName(recipe.getRecipeName());

			r.setCategory(recipe.getCategory().name());

			r.setPrepTime(recipe.getPreparationTime() + " mins");

			if (Boolean.TRUE.equals(recipe.getAvailable())) {
				r.setStatus("Available");
			} else {
				r.setStatus("Unavailable");
			}

			return r;

		}).toList();

		dto.setRecentRecipes(recentRecipes);
		List<ExpiryAlertDto> expiryAlerts = inventoryRepository.findTop5ByOrderByExpiryDateAsc().stream().map(item -> {

			ExpiryAlertDto e = new ExpiryAlertDto();

			e.setIngredient(item.getIngredientName());

			e.setQuantity(item.getQuantity());

			if (item.getExpiryDate().isBefore(LocalDate.now())) {

				e.setAlertStatus("Expired");

			} else if (item.getExpiryDate().isEqual(LocalDate.now())) {

				e.setAlertStatus("Expiring Today");

			} else {

				long days = LocalDate.now().until(item.getExpiryDate()).getDays();

				e.setAlertStatus("Expires in " + days + " days");

			}

			return e;

		}).toList();

		dto.setExpiryAlerts(expiryAlerts);
		return dto;
	}
}