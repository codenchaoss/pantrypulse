package com.pantrypulse.supplier.repository;

import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.supplier.entity.Supplier;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SupplierRepository extends JpaRepository<Supplier, Long> {

    List<Supplier> findBySupplierNameContainingIgnoreCase(String supplierName);

    List<Supplier> findByActive(Boolean active);

    // Owner-based methods
    List<Supplier> findByOwner(User owner);

    Optional<Supplier> findByIdAndOwner(Long id, User owner);

    List<Supplier> findByOwnerAndSupplierNameContainingIgnoreCase(User owner, String supplierName);

    List<Supplier> findByOwnerAndActive(User owner, Boolean active);

    long countByOwner(User owner);
}