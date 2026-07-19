package com.pantrypulse.supplier.service;



import com.pantrypulse.exception.ResourceNotFoundException;
import com.pantrypulse.supplier.dto.SupplierDto;
import com.pantrypulse.supplier.entity.Supplier;
import com.pantrypulse.supplier.mapper.SupplierMapper;
import com.pantrypulse.supplier.repository.SupplierRepository;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class SupplierService {

    private static final Logger logger =
            LoggerFactory.getLogger(SupplierService.class);

    private final SupplierRepository supplierRepository;

    public SupplierService(SupplierRepository supplierRepository) {
        this.supplierRepository = supplierRepository;
    }

    public SupplierDto addSupplier(SupplierDto dto) {

        logger.info("Creating supplier: {}", dto.getSupplierName());

        Supplier supplier = SupplierMapper.toEntity(dto);

        Supplier saved = supplierRepository.save(supplier);

        logger.info("Supplier created successfully with ID: {}", saved.getId());

        return SupplierMapper.toDto(saved);
    }

    public List<SupplierDto> getAllSuppliers() {

        logger.info("Fetching all suppliers");

        List<SupplierDto> suppliers = supplierRepository.findAll()
                .stream()
                .map(SupplierMapper::toDto)
                .collect(Collectors.toList());

        logger.info("Total suppliers fetched: {}", suppliers.size());

        return suppliers;
    }

    public SupplierDto getSupplierById(Long id) {

        logger.info("Fetching supplier with ID: {}", id);

        Supplier supplier = supplierRepository.findById(id)
                .orElseThrow(() -> {
                    logger.error("Supplier not found with ID: {}", id);
                    return new ResourceNotFoundException("Supplier not found with id " + id);
                });

        return SupplierMapper.toDto(supplier);
    }

    public SupplierDto updateSupplier(Long id, SupplierDto dto) {

        logger.info("Updating supplier with ID: {}", id);

        Supplier supplier = supplierRepository.findById(id)
                .orElseThrow(() -> {
                    logger.error("Supplier not found with ID: {}", id);
                    return new ResourceNotFoundException("Supplier not found with id " + id);
                });

        supplier.setSupplierName(dto.getSupplierName());
        supplier.setContactPerson(dto.getContactPerson());
        supplier.setPhone(dto.getPhone());
        supplier.setEmail(dto.getEmail());
        supplier.setAddress(dto.getAddress());
        supplier.setGstNumber(dto.getGstNumber());
        supplier.setActive(dto.getActive());

        Supplier updated = supplierRepository.save(supplier);

        logger.info("Supplier updated successfully with ID: {}", updated.getId());

        return SupplierMapper.toDto(updated);
    }

    public void deleteSupplier(Long id) {

        logger.info("Deleting supplier with ID: {}", id);

        Supplier supplier = supplierRepository.findById(id)
                .orElseThrow(() -> {
                    logger.error("Supplier not found with ID: {}", id);
                    return new ResourceNotFoundException("Supplier not found with id " + id);
                });

        supplierRepository.delete(supplier);

        logger.info("Supplier deleted successfully");
    }

    public List<SupplierDto> searchSupplier(String supplierName) {

        return supplierRepository
                .findBySupplierNameContainingIgnoreCase(supplierName)
                .stream()
                .map(SupplierMapper::toDto)
                .collect(Collectors.toList());
    }

    public List<SupplierDto> getActiveSuppliers(Boolean active) {

        return supplierRepository.findByActive(active)
                .stream()
                .map(SupplierMapper::toDto)
                .collect(Collectors.toList());
    }

}