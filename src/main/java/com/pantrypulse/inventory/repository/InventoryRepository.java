package com.pantrypulse.inventory.repository;

import java.time.LocalDate;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.pantrypulse.inventory.entity.Inventory;
@Repository
public interface InventoryRepository extends JpaRepository<Inventory, Long> {

    List<Inventory> findByIngredientNameContainingIgnoreCase(String ingredientName);

    List<Inventory> findByCategoryIgnoreCase(String category);

    List<Inventory> findByAvailable(Boolean available);
    List<Inventory> findTop5ByOrderByIdDesc();
    List<Inventory> findTop5ByOrderByExpiryDateAsc();
    

    @Query("""
            SELECT COUNT(i)
            FROM Inventory i
            WHERE i.quantity <= i.minimumStock
           """)
    long countLowStockItems();

    @Query("""
            SELECT COUNT(i)
            FROM Inventory i
            WHERE i.expiryDate BETWEEN CURRENT_DATE
            AND :date
           """)
    long countExpiringSoon(@Param("date") LocalDate date);

    @Query("""
            SELECT COUNT(i)
            FROM Inventory i
            WHERE i.expiryDate < CURRENT_DATE
           """)
    long countExpiredItems();
}