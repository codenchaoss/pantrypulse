package com.pantrypulse.recipeingredient.repository;

import com.pantrypulse.recipeingredient.entity.RecipeIngredient;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface RecipeIngredientRepository extends JpaRepository<RecipeIngredient, Long> {

    List<RecipeIngredient> findByRecipeId(Long recipeId);
    List<RecipeIngredient> findByInventoryId(Long inventoryId);
    

}