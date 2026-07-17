package com.pantrypulse.recipe.repository;

import com.pantrypulse.recipe.entity.Recipe;
import com.pantrypulse.recipe.enums.RecipeCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RecipeRepository extends JpaRepository<Recipe, Long> {

    List<Recipe> findByRecipeNameContainingIgnoreCase(String recipeName);

    List<Recipe> findByCategory(RecipeCategory category);

    List<Recipe> findByAvailable(Boolean available);
}