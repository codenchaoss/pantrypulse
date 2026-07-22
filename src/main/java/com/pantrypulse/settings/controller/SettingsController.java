package com.pantrypulse.settings.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.pantrypulse.settings.dto.AboutDto;
import com.pantrypulse.settings.dto.NotificationSettingsDto;
import com.pantrypulse.settings.dto.ProfileDto;
import com.pantrypulse.settings.service.SettingsService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/settings")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class SettingsController {

    private final SettingsService settingsService;

  

    @GetMapping("/profile")
    public ResponseEntity<ProfileDto> getProfile() {
        return ResponseEntity.ok(settingsService.getProfile());
    }

    @PutMapping("/profile")
    public ResponseEntity<ProfileDto> updateProfile(
            @RequestBody ProfileDto dto) {

        return ResponseEntity.ok(
                settingsService.updateProfile(dto)
        );
    }

 

    @GetMapping("/notifications")
    public ResponseEntity<NotificationSettingsDto> getNotifications() {

        return ResponseEntity.ok(
                settingsService.getNotifications()
        );
    }

    @PutMapping("/notifications")
    public ResponseEntity<NotificationSettingsDto> updateNotifications(
            @RequestBody NotificationSettingsDto dto) {

        return ResponseEntity.ok(
                settingsService.updateNotifications(dto)
        );
    }
  
    @GetMapping("/about")
    public ResponseEntity<AboutDto> getAbout() {

        return ResponseEntity.ok(
                settingsService.getAbout()
        );
    }
    

}