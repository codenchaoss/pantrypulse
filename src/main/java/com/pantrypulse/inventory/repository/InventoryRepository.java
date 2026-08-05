package com.pantrypulse.inventory.repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.inventory.entity.Inventory;
@Repository
public interface InventoryRepository extends JpaRepository<Inventory, Long> {

    List<Inventory> findByIngredientNameContainingIgnoreCase(String ingredientName);

    List<Inventory> findByCategoryIgnoreCase(String category);

    List<Inventory> findByAvailable(Boolean available);
    List<Inventory> findTop5ByOrderByIdDesc();
    List<Inventory> findTop5ByOrderByExpiryDateAsc();
    List<Inventory> findByOwner(User owner);

    List<Inventory> findByOwnerAndIngredientNameContainingIgnoreCase(User owner, String ingredientName);

    List<Inventory> findByOwnerAndCategoryIgnoreCase(User owner, String category);

    Optional<Inventory> findByIdAndOwner(Long id, User owner);
    long countByOwner(User owner);
    List<Inventory> findTop5ByOwnerOrderByIdDesc(User owner);

    List<Inventory> findTop5ByOwnerOrderByExpiryDateAsc(User owner);

    @Query("""
            SELECT COUNT(i)
            FROM Inventory i
            WHERE i.owner = :owner
              AND i.quantity <= i.minimumStock
           """)
    long countLowStockItems(@Param("owner") User owner);

    @Query("""
            SELECT COUNT(i)
            FROM Inventory i
            WHERE i.owner = :owner
              AND i.expiryDate BETWEEN CURRENT_DATE
              AND :date
           """)
    long countExpiringSoon(
            @Param("owner") User owner,
            @Param("date") LocalDate date);

    @Query("""
            SELECT COUNT(i)
            FROM Inventory i
            WHERE i.owner = :owner
              AND i.expiryDate < CURRENT_DATE
           """)
    long countExpiredItems(@Param("owner") User owner);
}