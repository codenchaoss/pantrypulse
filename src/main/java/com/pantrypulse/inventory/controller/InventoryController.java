package com.pantrypulse.inventory.controller;

import com.pantrypulse.inventory.dto.InventoryDto;
import com.pantrypulse.inventory.service.InventoryService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;
@Tag(
        name="Inventory API",
        description="Manage restaurant inventory."
)

@RestController
@RequestMapping("/api/inventory")
public class InventoryController {

    private final InventoryService inventoryService;

    public InventoryController(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public InventoryDto addIngredient(@Valid @RequestBody InventoryDto dto) {
        return inventoryService.addIngredient(dto);
    }
    @Operation(
    		summary="Get All Inventory Items",
    		description="Returns all inventory items that are availble."
    		)
    @GetMapping
    public List<InventoryDto> getAllIngredients() {
        return inventoryService.getAllIngredients();
    }
    @Operation(
    	    summary = "Get inventory by ID",
    	    description = "Returns a specific inventory item."
    	)

    @GetMapping("/{id}")
    public InventoryDto getIngredientById(@PathVariable Long id) {
        return inventoryService.getIngredientById(id);
    }

    @DeleteMapping("/{id}")
    public void deleteIngredient(@PathVariable Long id) {
        inventoryService.deleteIngredient(id);
    }
    @Operation(
    		summary="Get inventory items by search",
    		description="Returns inventory items matches with search."
    		)

    @GetMapping("/search")
    public List<InventoryDto> searchIngredient(@RequestParam String name) {
        return inventoryService.searchIngredient(name);
    }
    @PutMapping("/{id}")
    public InventoryDto updateIngredient(
            @PathVariable Long id,
            @Valid @RequestBody InventoryDto dto) {

        return inventoryService.updateIngredient(id, dto);
    }
    @Operation(
    		summary="Get Inventory items by category",
    		description="returns inventory items matching with given category"
    		)

    @GetMapping("/category/{category}")
    public List<InventoryDto> getByCategory(@PathVariable String category) {
        return inventoryService.getByCategory(category);
    }
}