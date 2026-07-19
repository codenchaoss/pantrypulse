package com.pantrypulse.historicalorder.repository;

import com.pantrypulse.historicalorder.entity.HistoricalOrder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface HistoricalOrderRepository extends JpaRepository<HistoricalOrder, Long> {

    List<HistoricalOrder> findByOrderDate(LocalDate orderDate);

    List<HistoricalOrder> findByRecipeId(Long recipeId);

    List<HistoricalOrder> findByOrderDateBetween(LocalDate startDate,
                                                 LocalDate endDate);
    long countByRecipeId(Long recipeId);
}