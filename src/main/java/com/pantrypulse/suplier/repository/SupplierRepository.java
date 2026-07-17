package com.pantrypulse.suplier.repository;

import com.pantrypulse.suplier.entity.Supplier;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SupplierRepository extends JpaRepository<Supplier, Long> {

    List<Supplier> findBySupplierNameContainingIgnoreCase(String supplierName);

    List<Supplier> findByActive(Boolean active);
}
