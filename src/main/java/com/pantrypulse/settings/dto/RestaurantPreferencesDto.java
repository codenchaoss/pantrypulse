package com.pantrypulse.settings.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RestaurantPreferencesDto {

    private String restaurantName;

    private String gstNumber;

    private String primaryContactEmail;

    private String primaryPhone;

    private String address;
}