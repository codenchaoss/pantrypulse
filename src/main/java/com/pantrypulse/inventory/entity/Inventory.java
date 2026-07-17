package com.pantrypulse.inventory.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import com.pantrypulse.recipeingredient.entity.RecipeIngredient;
import java.util.List;

@Entity
@Table(name = "inventory")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder

public class Inventory {
	 @Id
	    @GeneratedValue(strategy = GenerationType.IDENTITY)
	    private Long id;

	    private String ingredientName;

	    private Double quantity;

	    private String unit;

	    private String category;

	    private LocalDate expiryDate;

	    private Double minimumStock;

	    private Boolean available;
	    @OneToMany(mappedBy = "inventory")
	    private List<RecipeIngredient> recipes;

}
