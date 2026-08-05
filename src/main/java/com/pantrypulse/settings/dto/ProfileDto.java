package com.pantrypulse.settings.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProfileDto {

    private Long id;

    private String fullName;

    private String email;

    private String phoneNumber;

    private String role;

    private String restaurantName;

    private String profileImageUrl;
}