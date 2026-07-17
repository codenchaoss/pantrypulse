package com.pantrypulse.suplier.controller;

import com.pantrypulse.suplier.dto.SupplierDto;
import com.pantrypulse.suplier.service.SupplierService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/suppliers")
@CrossOrigin(origins = "*")
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

    @GetMapping
    public List<SupplierDto> getAllSuppliers() {
        return supplierService.getAllSuppliers();
    }

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

    @GetMapping("/search")
    public List<SupplierDto> searchSupplier(
            @RequestParam String name) {

        return supplierService.searchSupplier(name);
    }

    @GetMapping("/active/{active}")
    public List<SupplierDto> getActiveSuppliers(
            @PathVariable Boolean active) {

        return supplierService.getActiveSuppliers(active);
    }

}