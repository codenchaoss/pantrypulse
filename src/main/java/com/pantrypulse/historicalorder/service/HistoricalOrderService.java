package com.pantrypulse.historicalorder.service;

import com.pantrypulse.exception.ResourceNotFoundException;
import com.pantrypulse.historicalorder.dto.HistoricalOrderDto;
import com.pantrypulse.historicalorder.entity.HistoricalOrder;
import com.pantrypulse.historicalorder.mapper.HistoricalOrderMapper;
import com.pantrypulse.historicalorder.repository.HistoricalOrderRepository;
import com.pantrypulse.recipe.entity.Recipe;
import com.pantrypulse.recipe.repository.RecipeRepository;
import org.slf4j.Logger;
import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.authentication.service.AuthenticatedUserService;
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
    private final AuthenticatedUserService authenticatedUserService;
    public HistoricalOrderService(
            HistoricalOrderRepository historicalOrderRepository,
            RecipeRepository recipeRepository,
            AuthenticatedUserService authenticatedUserService) {

        this.historicalOrderRepository = historicalOrderRepository;
        this.recipeRepository = recipeRepository;
        this.authenticatedUserService = authenticatedUserService;
    }

    public HistoricalOrderDto addHistoricalOrder(HistoricalOrderDto dto) {

        logger.info("Creating historical order");

        User currentUser = authenticatedUserService.getCurrentUser();

        Recipe recipe = recipeRepository
                .findByIdAndOwner(dto.getRecipeId(), currentUser)
                .orElseThrow(() ->
                        new ResourceNotFoundException(
                                "Recipe not found"));

        HistoricalOrder order = HistoricalOrder.builder()
                .recipe(recipe)
                .quantity(dto.getQuantity())
                .orderDate(dto.getOrderDate())
                .owner(currentUser)
                .build();

        HistoricalOrder saved = historicalOrderRepository.save(order);

        logger.info("Historical order created with ID {}", saved.getId());

        return HistoricalOrderMapper.toDto(saved);
    }

    public List<HistoricalOrderDto> getAllHistoricalOrders() {

    	User currentUser = authenticatedUserService.getCurrentUser();

    	return historicalOrderRepository.findByOwner(currentUser)
    	        .stream()
    	        .map(HistoricalOrderMapper::toDto)
    	        .collect(Collectors.toList());
    }

    public HistoricalOrderDto getHistoricalOrderById(Long id) {

    	User currentUser = authenticatedUserService.getCurrentUser();

    	HistoricalOrder order =
    	        historicalOrderRepository.findByIdAndOwner(id, currentUser)
    	                .orElseThrow(() ->
    	                        new ResourceNotFoundException(
    	                                "Historical order not found"));

        return HistoricalOrderMapper.toDto(order);
    }

    public void deleteHistoricalOrder(Long id) {

    	User currentUser = authenticatedUserService.getCurrentUser();

    	HistoricalOrder order =
    	        historicalOrderRepository.findByIdAndOwner(id, currentUser)
    	                .orElseThrow(() ->
    	                        new ResourceNotFoundException(
    	                                "Historical order not found"));

        historicalOrderRepository.delete(order);
    }

}