package com.pantrypulse.recipe.repository;

import java.util.List;
import java.util.Optional;
import com.pantrypulse.authentication.entity.User;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import com.pantrypulse.recipe.entity.Recipe;
import com.pantrypulse.recipe.enums.RecipeCategory;


@Repository
public interface RecipeRepository extends JpaRepository<Recipe, Long> {

    List<Recipe> findByRecipeNameContainingIgnoreCase(String recipeName);

    List<Recipe> findByCategory(RecipeCategory category);

    List<Recipe> findByAvailable(Boolean available);

    List<Recipe> findTop5ByOrderByIdDesc();
    List<Recipe> findByOwner(User owner);

    Optional<Recipe> findByIdAndOwner(Long id, User owner);

    List<Recipe> findByOwnerAndRecipeNameContainingIgnoreCase(User owner, String recipeName);

    List<Recipe> findByOwnerAndCategory(User owner, RecipeCategory category);

    List<Recipe> findByOwnerAndAvailable(User owner, Boolean available);

    Page<Recipe> findByOwner(User owner, Pageable pageable);

    long countByOwner(User owner);

    List<Recipe> findTop5ByOwnerOrderByIdDesc(User owner);

}