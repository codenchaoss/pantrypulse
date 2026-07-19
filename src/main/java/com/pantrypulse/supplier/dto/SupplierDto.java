package com.pantrypulse.supplier.dto;

import jakarta.validation.constraints.*;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SupplierDto {

    private Long id;

    @NotBlank(message = "Supplier name is required")
    private String supplierName;

    @NotBlank(message = "Contact person is required")
    private String contactPerson;

    @NotBlank(message = "Phone number is required")
    private String phone;

    @Email(message = "Invalid email format")
    private String email;

    private String address;

    @NotBlank(message = "GST number is required")
    private String gstNumber;

    @NotNull(message = "Active status is required")
    private Boolean active;
}