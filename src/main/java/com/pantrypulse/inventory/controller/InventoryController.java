package com.pantrypulse.inventory.controller;

import com.pantrypulse.inventory.dto.InventoryDto;
import com.pantrypulse.inventory.service.InventoryService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/inventory")
@CrossOrigin(origins = "*")
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

    @GetMapping
    public List<InventoryDto> getAllIngredients() {
        return inventoryService.getAllIngredients();
    }

    @GetMapping("/{id}")
    public InventoryDto getIngredientById(@PathVariable Long id) {
        return inventoryService.getIngredientById(id);
    }

    @DeleteMapping("/{id}")
    public void deleteIngredient(@PathVariable Long id) {
        inventoryService.deleteIngredient(id);
    }

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

    @GetMapping("/category/{category}")
    public List<InventoryDto> getByCategory(@PathVariable String category) {
        return inventoryService.getByCategory(category);
    }
}