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

        System.out.println("========================");
        System.out.println("EMAIL METHOD CALLED");
        System.out.println(email);
        System.out.println(resetLink);
        System.out.println("========================");

        // DO NOT SEND MAIL
    }
}