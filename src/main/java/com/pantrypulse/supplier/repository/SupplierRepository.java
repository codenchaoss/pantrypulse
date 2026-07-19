package com.pantrypulse.supplier.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.pantrypulse.supplier.entity.Supplier;

import java.util.List;

@Repository
public interface SupplierRepository extends JpaRepository<Supplier, Long> {

    List<Supplier> findBySupplierNameContainingIgnoreCase(String supplierName);

    List<Supplier> findByActive(Boolean active);
}
