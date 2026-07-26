package com.pantrypulse.historicalorder.repository;
import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.historicalorder.entity.HistoricalOrder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface HistoricalOrderRepository extends JpaRepository<HistoricalOrder, Long> {

    List<HistoricalOrder> findByOrderDate(LocalDate orderDate);

    List<HistoricalOrder> findByRecipeId(Long recipeId);

    List<HistoricalOrder> findByOrderDateBetween(LocalDate startDate,
                                                 LocalDate endDate);
    long countByRecipeId(Long recipeId);
    List<HistoricalOrder> findByOwner(User owner);

    Optional<HistoricalOrder> findByIdAndOwner(Long id, User owner);

    List<HistoricalOrder> findByOwnerAndOrderDate(User owner, LocalDate orderDate);

    List<HistoricalOrder> findByOwnerAndRecipeId(User owner, Long recipeId);

    List<HistoricalOrder> findByOwnerAndOrderDateBetween(
            User owner,
            LocalDate startDate,
            LocalDate endDate);

    long countByOwner(User owner);
}