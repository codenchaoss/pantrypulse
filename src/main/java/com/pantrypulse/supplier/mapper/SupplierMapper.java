package com.pantrypulse.supplier.mapper;

import com.pantrypulse.supplier.dto.SupplierDto;
import com.pantrypulse.supplier.entity.Supplier;

public class SupplierMapper {

    public static SupplierDto toDto(Supplier supplier) {

        return SupplierDto.builder()
                .id(supplier.getId())
                .supplierName(supplier.getSupplierName())
                .contactPerson(supplier.getContactPerson())
                .phone(supplier.getPhone())
                .email(supplier.getEmail())
                .address(supplier.getAddress())
                .gstNumber(supplier.getGstNumber())
                .active(supplier.getActive())
                .build();
    }

    public static Supplier toEntity(SupplierDto dto) {

        return Supplier.builder()
                .id(dto.getId())
                .supplierName(dto.getSupplierName())
                .contactPerson(dto.getContactPerson())
                .phone(dto.getPhone())
                .email(dto.getEmail())
                .address(dto.getAddress())
                .gstNumber(dto.getGstNumber())
                .active(dto.getActive())
                .build();
    }
}