package com.pantrypulse.authentication.controller;

import org.springframework.web.bind.annotation.*;

import com.pantrypulse.authentication.dto.AuthResponse;
import com.pantrypulse.authentication.dto.LoginRequest;
import com.pantrypulse.authentication.dto.RegisterRequest;
import com.pantrypulse.authentication.service.AuthService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/register")
    public String register(@RequestBody RegisterRequest request) {
        return authService.register(request);
    }

    @PostMapping("/login")
    public AuthResponse login(@RequestBody LoginRequest request) {
        return authService.login(request);
    }
}