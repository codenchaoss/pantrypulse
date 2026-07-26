package com.pantrypulse.recipe.service;

import com.pantrypulse.exception.ResourceNotFoundException;
import com.pantrypulse.recipe.dto.RecipeDto;
import com.pantrypulse.recipe.entity.Recipe;
import com.pantrypulse.recipe.enums.RecipeCategory;
import com.pantrypulse.recipe.mapper.RecipeMapper;
import com.pantrypulse.recipe.repository.RecipeRepository;
import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.authentication.service.AuthenticatedUserService;
import org.slf4j.LoggerFactory;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import java.util.stream.Collectors;

@Service
public class RecipeService {
	private static final Logger logger =
	        LoggerFactory.getLogger(RecipeService.class);

    private final RecipeRepository recipeRepository;
    private final AuthenticatedUserService authenticatedUserService;

    public RecipeService(
            RecipeRepository recipeRepository,
            AuthenticatedUserService authenticatedUserService) {

        this.recipeRepository = recipeRepository;
        this.authenticatedUserService = authenticatedUserService;
    }

    public RecipeDto addRecipe(RecipeDto dto) {

        logger.info("Creating recipe: {}", dto.getRecipeName());

        User currentUser = authenticatedUserService.getCurrentUser();

        Recipe recipe = RecipeMapper.toEntity(dto);

        recipe.setOwner(currentUser);

        Recipe saved = recipeRepository.save(recipe);

        logger.info("Recipe created successfully with ID: {}", saved.getId());

        return RecipeMapper.toDto(saved);
    }

    public List<RecipeDto> getAllRecipes() {

        logger.info("Fetching all recipes");

        User currentUser = authenticatedUserService.getCurrentUser();

        List<RecipeDto> recipes = recipeRepository.findByOwner(currentUser)
                .stream()
                .map(RecipeMapper::toDto)
                .collect(Collectors.toList());

        logger.info("Total recipes fetched: {}", recipes.size());

        return recipes;
    }

    public RecipeDto getRecipeById(Long id) {

        logger.info("Fetching recipe with ID: {}", id);

        User currentUser = authenticatedUserService.getCurrentUser();

        Recipe recipe = recipeRepository.findByIdAndOwner(id, currentUser)
                .orElseThrow(() -> {
                    logger.error("Recipe not found with ID: {}", id);
                    return new ResourceNotFoundException("Recipe not found with id " + id);
                });

        logger.info("Recipe fetched successfully with ID: {}", recipe.getId());

        return RecipeMapper.toDto(recipe);
    }
    
    public RecipeDto updateRecipe(Long id, RecipeDto dto) {

        logger.info("Updating recipe with ID: {}", id);

        User currentUser = authenticatedUserService.getCurrentUser();

        Recipe recipe = recipeRepository.findByIdAndOwner(id, currentUser)
                .orElseThrow(() -> {
                    logger.error("Recipe not found with ID: {}", id);
                    return new ResourceNotFoundException("Recipe not found with id " + id);
                });

        recipe.setRecipeName(dto.getRecipeName());
        recipe.setCategory(dto.getCategory());
        recipe.setDescription(dto.getDescription());
        recipe.setPreparationTime(dto.getPreparationTime());
        recipe.setServings(dto.getServings());
        recipe.setCostPrice(dto.getCostPrice());
        recipe.setSellingPrice(dto.getSellingPrice());
        recipe.setCalories(dto.getCalories());
        recipe.setAvailable(dto.getAvailable());

        Recipe updated = recipeRepository.save(recipe);

        logger.info("Recipe updated successfully with ID: {}", updated.getId());

        return RecipeMapper.toDto(updated);
    }
    public void deleteRecipe(Long id) {

        logger.info("Deleting recipe with ID: {}", id);

        User currentUser = authenticatedUserService.getCurrentUser();

        Recipe recipe = recipeRepository.findByIdAndOwner(id, currentUser)
                .orElseThrow(() -> {
                    logger.error("Recipe not found with ID: {}", id);
                    return new ResourceNotFoundException("Recipe not found");
                });

        recipeRepository.delete(recipe);

        logger.info("Recipe deleted successfully with ID: {}", id);
    }
    public List<RecipeDto> searchRecipe(String recipeName) {

        User currentUser = authenticatedUserService.getCurrentUser();

        return recipeRepository
                .findByOwnerAndRecipeNameContainingIgnoreCase(currentUser, recipeName)
                .stream()
                .map(RecipeMapper::toDto)
                .collect(Collectors.toList());
    }

    public List<RecipeDto> getByCategory(RecipeCategory category) {

        User currentUser = authenticatedUserService.getCurrentUser();

        return recipeRepository
                .findByOwnerAndCategory(currentUser, category)
                .stream()
                .map(RecipeMapper::toDto)
                .collect(Collectors.toList());
    }

    public List<RecipeDto> getAvailableRecipes(Boolean available) {

        User currentUser = authenticatedUserService.getCurrentUser();

        return recipeRepository
                .findByOwnerAndAvailable(currentUser, available)
                .stream()
                .map(RecipeMapper::toDto)
                .collect(Collectors.toList());
    }
    public Page<RecipeDto> getAllRecipes(Pageable pageable) {

        logger.info("Fetching recipes - Page: {}, Size: {}",
                pageable.getPageNumber(),
                pageable.getPageSize());

        User currentUser = authenticatedUserService.getCurrentUser();

        Page<RecipeDto> recipes = recipeRepository
                .findByOwner(currentUser, pageable)
                .map(RecipeMapper::toDto);

        logger.info("Fetched {} recipes",
                recipes.getNumberOfElements());

        return recipes;
    }
}