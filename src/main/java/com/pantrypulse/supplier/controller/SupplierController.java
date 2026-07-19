package com.pantrypulse.supplier.controller;

import com.pantrypulse.supplier.dto.SupplierDto;
import com.pantrypulse.supplier.service.SupplierService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;
@Tag(
        name="Supplier API",
        description="Manage supplier information."
)

@RestController
@RequestMapping("/api/suppliers")
public class SupplierController {

    private final SupplierService supplierService;

    public SupplierController(SupplierService supplierService) {
        this.supplierService = supplierService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public SupplierDto addSupplier(@Valid @RequestBody SupplierDto dto) {
        return supplierService.addSupplier(dto);
    }
    @Operation(
    		summary="Get All Suppliers",
    		description="Returns all suppliers ."
    		)

    @GetMapping
    public List<SupplierDto> getAllSuppliers() {
        return supplierService.getAllSuppliers();
    }
    @Operation(
    	    summary = "Get Supplier By ID",
    	    description = "Returns a specific supplier."
    	)
    @GetMapping("/{id}")
    public SupplierDto getSupplierById(@PathVariable Long id) {
        return supplierService.getSupplierById(id);
    }

    @PutMapping("/{id}")
    public SupplierDto updateSupplier(
            @PathVariable Long id,
            @Valid @RequestBody SupplierDto dto) {

        return supplierService.updateSupplier(id, dto);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteSupplier(@PathVariable Long id) {
        supplierService.deleteSupplier(id);
    }
    @Operation(
    		summary="Search Suppliers",
    		description="Returns suppliers that matches search category."
    		)

    @GetMapping("/search")
    public List<SupplierDto> searchSupplier(
            @RequestParam String name) {

        return supplierService.searchSupplier(name);
    }
    @Operation(
    		summary="Get Active Suppliers",
    		description="Returns all active suppliers availble."
    		)

    @GetMapping("/active/{active}")
    public List<SupplierDto> getActiveSuppliers(
            @PathVariable Boolean active) {

        return supplierService.getActiveSuppliers(active);
    }

}