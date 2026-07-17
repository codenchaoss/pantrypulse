package com.pantrypulse.recipe.entity;

import com.pantrypulse.recipe.enums.RecipeCategory;
import jakarta.persistence.*;
import com.pantrypulse.recipeingredient.entity.RecipeIngredient;
import java.util.List;
import lombok.*;

@Entity
@Table(name = "recipes")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Recipe {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String recipeName;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RecipeCategory category;

    @Column(length = 500)
    private String description;

    private Integer preparationTime;

    private Integer servings;

    private Double costPrice;

    private Double sellingPrice;

    private Integer calories;

    private Boolean available;
    @OneToMany(mappedBy = "recipe",
            cascade = CascadeType.ALL,
            orphanRemoval = true)
    private List<RecipeIngredient> ingredients;
}