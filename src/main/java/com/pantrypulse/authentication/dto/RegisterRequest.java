package com.pantrypulse.authentication.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
public class RegisterRequest {

    @Schema(requiredMode = Schema.RequiredMode.REQUIRED, example = "Admin")
    private String name;

    @Schema(requiredMode = Schema.RequiredMode.REQUIRED, example = "admin@pantrypulse.com")
    private String email;

    @Schema(requiredMode = Schema.RequiredMode.REQUIRED, example = "Admin@123")
    private String password;
}