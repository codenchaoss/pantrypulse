package com.pantrypulse.authentication.service;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class EmailService {

    private final RestClient restClient;

    @Value("${brevo.api.key}")
    private String apiKey;

    @Value("${brevo.sender.email}")
    private String senderEmail;

    @Value("${brevo.sender.name}")
    private String senderName;

    public void sendPasswordResetEmail(String toEmail, String resetLink) {

        Map<String, Object> body = Map.of(
                "sender", Map.of(
                        "name", senderName,
                        "email", senderEmail
                ),
                "to", new Object[]{
                        Map.of("email", toEmail)
                },
                "subject", "PantryPulse Password Reset",
                "htmlContent",
                """
                <h2>Reset your password</h2>
                <p>Click the button below to reset your password:</p>
                <a href="%s"
                   style="padding:12px 20px;
                          background:#4CAF50;
                          color:white;
                          text-decoration:none;
                          border-radius:5px;">
                    Reset Password
                </a>
                """.formatted(resetLink)
        );

        restClient.post()
                .uri("https://api.brevo.com/v3/smtp/email")
                .contentType(MediaType.APPLICATION_JSON)
                .header("api-key", apiKey)
                .body(body)
                .retrieve()
                .toBodilessEntity();
    }
}