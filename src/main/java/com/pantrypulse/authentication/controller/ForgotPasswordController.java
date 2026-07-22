package com.pantrypulse.authentication.controller;

import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.pantrypulse.authentication.dto.ForgotPasswordRequest;
import com.pantrypulse.authentication.dto.ResetPasswordRequest;
import com.pantrypulse.authentication.service.PasswordResetService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class ForgotPasswordController {

    private final PasswordResetService passwordResetService;
    @PostMapping("/forgot-password")
    public ResponseEntity<Map<String, String>> forgotPassword(
            @RequestBody ForgotPasswordRequest request) {

        String message = passwordResetService.forgotPassword(request);

        return ResponseEntity.ok(
            Map.of("message", message)
        );
    }
    @PostMapping("/reset-password")
    public ResponseEntity<String> resetPassword(
            @Valid @RequestBody ResetPasswordRequest request) {

        return ResponseEntity.ok(
                passwordResetService.resetPassword(request));
    }
}