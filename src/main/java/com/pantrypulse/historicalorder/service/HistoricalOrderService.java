package com.pantrypulse.historicalorder.service;

import com.pantrypulse.exception.ResourceNotFoundException;
import com.pantrypulse.historicalorder.dto.HistoricalOrderDto;
import com.pantrypulse.historicalorder.entity.HistoricalOrder;
import com.pantrypulse.historicalorder.mapper.HistoricalOrderMapper;
import com.pantrypulse.historicalorder.repository.HistoricalOrderRepository;
import com.pantrypulse.recipe.entity.Recipe;
import com.pantrypulse.recipe.repository.RecipeRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class HistoricalOrderService {

    private static final Logger logger =
            LoggerFactory.getLogger(HistoricalOrderService.class);

    private final HistoricalOrderRepository historicalOrderRepository;
    private final RecipeRepository recipeRepository;

    public HistoricalOrderService(HistoricalOrderRepository historicalOrderRepository,
                                  RecipeRepository recipeRepository) {
        this.historicalOrderRepository = historicalOrderRepository;
        this.recipeRepository = recipeRepository;
    }

    public HistoricalOrderDto addHistoricalOrder(HistoricalOrderDto dto) {

        logger.info("Creating historical order");

        Recipe recipe = recipeRepository.findById(dto.getRecipeId())
                .orElseThrow(() ->
                        new ResourceNotFoundException(
                                "Recipe not found with id " + dto.getRecipeId()));

        HistoricalOrder order = HistoricalOrder.builder()
                .recipe(recipe)
                .quantity(dto.getQuantity())
                .orderDate(dto.getOrderDate())
                .build();

        HistoricalOrder saved = historicalOrderRepository.save(order);

        logger.info("Historical order created with ID {}", saved.getId());

        return HistoricalOrderMapper.toDto(saved);
    }

    public List<HistoricalOrderDto> getAllHistoricalOrders() {

        return historicalOrderRepository.findAll()
                .stream()
                .map(HistoricalOrderMapper::toDto)
                .collect(Collectors.toList());
    }

    public HistoricalOrderDto getHistoricalOrderById(Long id) {

        HistoricalOrder order = historicalOrderRepository.findById(id)
                .orElseThrow(() ->
                        new ResourceNotFoundException(
                                "Historical order not found with id " + id));

        return HistoricalOrderMapper.toDto(order);
    }

    public void deleteHistoricalOrder(Long id) {

        HistoricalOrder order = historicalOrderRepository.findById(id)
                .orElseThrow(() ->
                        new ResourceNotFoundException(
                                "Historical order not found with id " + id));

        historicalOrderRepository.delete(order);
    }

}