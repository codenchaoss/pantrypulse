package com.pantrypulse.dashboard.dto;

import lombok.Data;

@Data
public class ExpiryAlertDto {

    private String ingredient;

    private Double quantity;

    private String alertStatus;

}