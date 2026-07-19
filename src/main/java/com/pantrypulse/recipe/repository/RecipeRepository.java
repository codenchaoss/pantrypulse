package com.pantrypulse.recipe.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.pantrypulse.recipe.entity.Recipe;
import com.pantrypulse.recipe.enums.RecipeCategory;

@Repository
public interface RecipeRepository extends JpaRepository<Recipe, Long> {

    List<Recipe> findByRecipeNameContainingIgnoreCase(String recipeName);

    List<Recipe> findByCategory(RecipeCategory category);

    List<Recipe> findByAvailable(Boolean available);

    List<Recipe> findTop5ByOrderByIdDesc();

}