package com.pantrypulse.inventory.repository;

import com.pantrypulse.inventory.entity.Inventory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
@Repository
public interface InventoryRepository  extends JpaRepository<Inventory, Long> {

	  List<Inventory> findByIngredientNameContainingIgnoreCase(String ingredientName);

	    List<Inventory> findByCategoryIgnoreCase(String category);

	    List<Inventory> findByAvailable(Boolean available);
}
