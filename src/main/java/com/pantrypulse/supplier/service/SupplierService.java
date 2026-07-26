package com.pantrypulse.supplier.service;



import com.pantrypulse.exception.ResourceNotFoundException;
import com.pantrypulse.supplier.dto.SupplierDto;
import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.authentication.service.AuthenticatedUserService;
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
    private final AuthenticatedUserService authenticatedUserService;
    public SupplierService(
            SupplierRepository supplierRepository,
            AuthenticatedUserService authenticatedUserService) {

        this.supplierRepository = supplierRepository;
        this.authenticatedUserService = authenticatedUserService;
    }
    public SupplierDto addSupplier(SupplierDto dto) {

        logger.info("Creating supplier: {}", dto.getSupplierName());

        User currentUser = authenticatedUserService.getCurrentUser();

        Supplier supplier = SupplierMapper.toEntity(dto);

        supplier.setOwner(currentUser);

        Supplier saved = supplierRepository.save(supplier);

        logger.info("Supplier created successfully with ID: {}", saved.getId());

        return SupplierMapper.toDto(saved);
    }

    public List<SupplierDto> getAllSuppliers() {

        logger.info("Fetching all suppliers");

        User currentUser = authenticatedUserService.getCurrentUser();

        List<SupplierDto> suppliers = supplierRepository
                .findByOwner(currentUser)
                .stream()
                .map(SupplierMapper::toDto)
                .collect(Collectors.toList());

        logger.info("Total suppliers fetched: {}", suppliers.size());

        return suppliers;
    }

    public SupplierDto getSupplierById(Long id) {

        logger.info("Fetching supplier with ID: {}", id);

        User currentUser = authenticatedUserService.getCurrentUser();

        Supplier supplier = supplierRepository.findByIdAndOwner(id, currentUser)
                .orElseThrow(() -> {
                    logger.error("Supplier not found with ID: {}", id);
                    return new ResourceNotFoundException("Supplier not found with id " + id);
                });

        return SupplierMapper.toDto(supplier);
    }

    public SupplierDto updateSupplier(Long id, SupplierDto dto) {

        logger.info("Updating supplier with ID: {}", id);

        User currentUser = authenticatedUserService.getCurrentUser();

        Supplier supplier = supplierRepository.findByIdAndOwner(id, currentUser)
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

        User currentUser = authenticatedUserService.getCurrentUser();

        Supplier supplier = supplierRepository.findByIdAndOwner(id, currentUser)
                .orElseThrow(() -> {
                    logger.error("Supplier not found with ID: {}", id);
                    return new ResourceNotFoundException("Supplier not found with id " + id);
                });

        supplierRepository.delete(supplier);

        logger.info("Supplier deleted successfully");
    }

    public List<SupplierDto> searchSupplier(String supplierName) {

        User currentUser = authenticatedUserService.getCurrentUser();

        return supplierRepository
                .findByOwnerAndSupplierNameContainingIgnoreCase(currentUser, supplierName)
                .stream()
                .map(SupplierMapper::toDto)
                .collect(Collectors.toList());
    }
    public List<SupplierDto> getActiveSuppliers(Boolean active) {

        User currentUser = authenticatedUserService.getCurrentUser();

        return supplierRepository
                .findByOwnerAndActive(currentUser, active)
                .stream()
                .map(SupplierMapper::toDto)
                .collect(Collectors.toList());
    }

}