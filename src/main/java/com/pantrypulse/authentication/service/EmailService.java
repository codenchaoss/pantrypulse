package com.pantrypulse.authentication.service;

import lombok.RequiredArgsConstructor;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
@Service
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender mailSender;

    public void sendPasswordResetEmail(String email, String resetLink) {

        try {

            SimpleMailMessage message = new SimpleMailMessage();

            message.setFrom("jaswanthvennapusa25@gmail.com");

            message.setTo(email);

            message.setSubject("PantryPulse Password Reset");

            message.setText(resetLink);

            mailSender.send(message);

            System.out.println("MAIL SENT SUCCESSFULLY");

        } catch (Exception e) {

            e.printStackTrace();

            throw e;
        }
    }
}