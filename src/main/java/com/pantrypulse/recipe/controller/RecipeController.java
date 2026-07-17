package com.pantrypulse.recipe.controller;

import com.pantrypulse.recipe.dto.RecipeDto;
import com.pantrypulse.recipe.enums.RecipeCategory;
import com.pantrypulse.recipe.service.RecipeService;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/recipes")
@CrossOrigin(origins = "*")
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

    @GetMapping
    public Page<RecipeDto> getAllRecipes(Pageable pageable) {

        return recipeService.getAllRecipes(pageable);
    }

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

    @GetMapping("/search")
    public List<RecipeDto> searchRecipe(@RequestParam String name) {
        return recipeService.searchRecipe(name);
    }

    @GetMapping("/category/{category}")
    public List<RecipeDto> getByCategory(@PathVariable RecipeCategory category) {
        return recipeService.getByCategory(category);
    }

    @GetMapping("/available/{available}")
    public List<RecipeDto> getAvailableRecipes(@PathVariable Boolean available) {
        return recipeService.getAvailableRecipes(available);
    }
}