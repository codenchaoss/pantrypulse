package com.pantrypulse.recommendation.engine;

import com.pantrypulse.inventory.entity.Inventory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;

@Component
public class ExpirationEngine {

    private static final ZoneId APP_ZONE =
            ZoneId.of("Asia/Kolkata");

    @Value("${recommendation.expiry-threshold-days}")
    private long expiryThreshold;

    public long calculateDaysRemaining(Inventory inventory) {

        return ChronoUnit.DAYS.between(
                LocalDate.now(APP_ZONE),
                inventory.getExpiryDate()
        );
    }

    public boolean isExpiringSoon(Inventory inventory) {

        long days = calculateDaysRemaining(inventory);

        return days <= expiryThreshold;
    }
}