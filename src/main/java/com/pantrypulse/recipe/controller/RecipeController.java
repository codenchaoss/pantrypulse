package com.pantrypulse.recipe.controller;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import com.pantrypulse.recipe.dto.RecipeDto;
import com.pantrypulse.recipe.enums.RecipeCategory;
import com.pantrypulse.recipe.service.RecipeService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
@Tag(
        name="Recipe API",
        description="Manage restaurant recipes.."
)


@RestController
@RequestMapping("/api/recipes")
public class RecipeController {

    private final RecipeService recipeService;

    public RecipeController(RecipeService recipeService) {
        this.recipeService = recipeService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public RecipeDto addRecipe(@Valid @RequestBody RecipeDto dto) {
        return recipeService.addRecipe(dto);
    }
    @Operation(
    		summary="Get All Recipes",
    		description="Returns recipes that are availble."
    		)
    @GetMapping
    public Page<RecipeDto> getAllRecipes(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "100") int size) {

        Pageable pageable = PageRequest.of(page, size);

        return recipeService.getAllRecipes(pageable);
    }
    @Operation(
    	    summary = "Get Recipe by ID",
    	    description = "Returns a specific Recipe ."
    	)

    @GetMapping("/{id}")
    public RecipeDto getRecipeById(@PathVariable Long id) {
        return recipeService.getRecipeById(id);
    }

    @PutMapping("/{id}")
    public RecipeDto updateRecipe(
            @PathVariable Long id,
            @Valid @RequestBody RecipeDto dto) {

        return recipeService.updateRecipe(id, dto);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteRecipe(@PathVariable Long id) {
        recipeService.deleteRecipe(id);
    }
    @Operation(
    		summary="Search Recipes",
    		description="Returns recipes that matches the search."
    		)

    @GetMapping("/search")
    public List<RecipeDto> searchRecipe(@RequestParam String name) {
        return recipeService.searchRecipe(name);
    }
    @Operation(
    		summary="Get Recipes By Category",
    		description="Returns recipes that matches the category."
    		)

    @GetMapping("/category/{category}")
    public List<RecipeDto> getByCategory(@PathVariable RecipeCategory category) {
        return recipeService.getByCategory(category);
    }
    @Operation(
    		summary="Get Available Recipes",
    		description="Returns all availble recipes."
    		)
    @GetMapping("/available/{available}")
    public List<RecipeDto> getAvailableRecipes(@PathVariable Boolean available) {
        return recipeService.getAvailableRecipes(available);
    }
}