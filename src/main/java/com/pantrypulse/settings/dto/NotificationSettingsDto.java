package com.pantrypulse.settings.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class NotificationSettingsDto {

    private Boolean lowStockAlerts;

    private Boolean expiryAlerts;

    private Boolean aiMenuNotifications;

    private Boolean emailNotifications;
}