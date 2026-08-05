package com.pantrypulse.authentication.service;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.pantrypulse.authentication.dto.ForgotPasswordRequest;
import com.pantrypulse.authentication.dto.ResetPasswordRequest;
import com.pantrypulse.authentication.entity.PasswordResetToken;
import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.authentication.repository.PasswordResetTokenRepository;
import com.pantrypulse.authentication.repository.UserRepository;
import com.pantrypulse.exception.ResourceNotFoundException;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class PasswordResetService {

    private static final ZoneId APP_ZONE =
            ZoneId.of("Asia/Kolkata");

    private final UserRepository userRepository;
    private final PasswordResetTokenRepository tokenRepository;
    private final PasswordEncoder passwordEncoder;
    private final EmailService emailService;

    @Value("${frontend.url}")
    private String frontendUrl;

    @Transactional
    public String forgotPassword(ForgotPasswordRequest request) {

        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() ->
                        new ResourceNotFoundException("User not found."));

        PasswordResetToken passwordResetToken =
                tokenRepository.findByUser(user)
                        .orElse(new PasswordResetToken());

        passwordResetToken.setUser(user);
        passwordResetToken.setToken(UUID.randomUUID().toString());

        passwordResetToken.setExpiryDate(
                LocalDateTime.now(APP_ZONE).plusMinutes(30)
        );

        tokenRepository.save(passwordResetToken);

        String resetLink =
                frontendUrl
                + "/reset-password?token="
                + passwordResetToken.getToken();

        emailService.sendPasswordResetEmail(
                user.getEmail(),
                resetLink
        );

        return "Password reset link sent successfully.";
    }

    public String resetPassword(ResetPasswordRequest request) {

        PasswordResetToken token =
                tokenRepository.findByToken(request.getToken())
                        .orElseThrow(() ->
                                new IllegalArgumentException(
                                        "Invalid reset token."));

        if (token.getExpiryDate()
                .isBefore(LocalDateTime.now(APP_ZONE))) {

            tokenRepository.delete(token);

            throw new IllegalArgumentException(
                    "Reset token has expired.");
        }

        User user = token.getUser();

        user.setPassword(
                passwordEncoder.encode(
                        request.getNewPassword())
        );

        userRepository.save(user);

        tokenRepository.delete(token);

        return "Password updated successfully.";
    }
}