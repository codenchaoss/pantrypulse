package com.pantrypulse.inventory.service;

import com.pantrypulse.inventory.dto.InventoryDto;
import com.pantrypulse.inventory.entity.Inventory;
import com.pantrypulse.inventory.mapper.InventoryMapper;
import com.pantrypulse.inventory.repository.InventoryRepository;
import com.pantrypulse.exception.ResourceNotFoundException;
import org.springframework.stereotype.Service;
import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.authentication.service.AuthenticatedUserService;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class InventoryService {

    private final InventoryRepository inventoryRepository;

    
    private final AuthenticatedUserService authenticatedUserService;

    public InventoryService(
            InventoryRepository inventoryRepository,
            AuthenticatedUserService authenticatedUserService) {

        this.inventoryRepository = inventoryRepository;
        this.authenticatedUserService = authenticatedUserService;
    }

    public InventoryDto addIngredient(InventoryDto dto) {

        User currentUser = authenticatedUserService.getCurrentUser();

        Inventory inventory = InventoryMapper.toEntity(dto);

        inventory.setOwner(currentUser);

        Inventory saved = inventoryRepository.save(inventory);

        return InventoryMapper.toDto(saved);
    }

    public List<InventoryDto> getAllIngredients() {

        User currentUser = authenticatedUserService.getCurrentUser();

        return inventoryRepository.findByOwner(currentUser)
                .stream()
                .map(InventoryMapper::toDto)
                .collect(Collectors.toList());
    }

    public InventoryDto getIngredientById(Long id) {

        User currentUser = authenticatedUserService.getCurrentUser();

        Inventory inventory = inventoryRepository
                .findByIdAndOwner(id, currentUser)
                .orElseThrow(() ->
                        new ResourceNotFoundException("Ingredient not found"));

        return InventoryMapper.toDto(inventory);
    }
    public void deleteIngredient(Long id) {

        Inventory inventory = inventoryRepository.findById(id)
                .orElseThrow(() ->
                        new ResourceNotFoundException("Ingredient not found with id " + id));

        inventoryRepository.delete(inventory);
    }

    public List<InventoryDto> searchIngredient(String name) {

        return inventoryRepository
                .findByIngredientNameContainingIgnoreCase(name)
                .stream()
                .map(InventoryMapper::toDto)
                .collect(Collectors.toList());
    }
    public InventoryDto updateIngredient(Long id, InventoryDto dto) {

        Inventory inventory = inventoryRepository.findById(id)
                .orElseThrow(() ->
                        new ResourceNotFoundException("Ingredient not found with id " + id));

        inventory.setIngredientName(dto.getIngredientName());
        inventory.setQuantity(dto.getQuantity());
        inventory.setUnit(dto.getUnit());
        inventory.setCategory(dto.getCategory());
        inventory.setExpiryDate(dto.getExpiryDate());
        inventory.setMinimumStock(dto.getMinimumStock());
        inventory.setAvailable(dto.getAvailable());

        Inventory updated = inventoryRepository.save(inventory);

        return InventoryMapper.toDto(updated);
    }

    public List<InventoryDto> getByCategory(String category) {

        return inventoryRepository
                .findByCategoryIgnoreCase(category)
                .stream()
                .map(InventoryMapper::toDto)
                .collect(Collectors.toList());
    }
}