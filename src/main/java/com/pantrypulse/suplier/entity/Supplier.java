package com.pantrypulse.suplier.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "suppliers")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Supplier {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String supplierName;

    @Column(nullable = false)
    private String contactPerson;

    @Column(nullable = false, unique = true)
    private String phone;

    @Column(unique = true)
    private String email;

    private String address;

    @Column(unique = true)
    private String gstNumber;

    @Column(nullable = false)
    private Boolean active;
}