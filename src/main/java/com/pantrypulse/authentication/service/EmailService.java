package com.pantrypulse.authentication.service;

import lombok.RequiredArgsConstructor;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;


@Service
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender mailSender;

    public void sendPasswordResetEmail(String email, String resetLink) {

        SimpleMailMessage message = new SimpleMailMessage();

        message.setTo(email);
        message.setSubject("PantryPulse Password Reset");

        message.setText(
                "Hello,\n\n"
                + "Click the link below to reset your password:\n\n"
                + resetLink
                + "\n\nThis link expires in 30 minutes.\n\n"
                + "PantryPulse Team"
        );

        mailSender.send(message);
    }
}