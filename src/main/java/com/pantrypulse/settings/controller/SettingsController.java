package com.pantrypulse.settings.controller;

import com.pantrypulse.settings.dto.*;
import com.pantrypulse.settings.service.SettingsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/settings")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class SettingsController {

    private final SettingsService settingsService;


    @GetMapping("/profile")
    public ProfileDto getProfile() {
        return settingsService.getProfile();
    }
    @PutMapping("/profile")
    public ProfileDto updateProfile(@RequestBody ProfileDto dto) {

        return settingsService.updateProfile(dto);
    }

    @GetMapping("/notifications")
    public NotificationSettingsDto getNotifications() {
        return settingsService.getNotifications();
    }
    @PutMapping("/notifications")
    public NotificationSettingsDto updateNotifications(
            @RequestBody NotificationSettingsDto dto) {

        return settingsService.updateNotifications(dto);
    }
    @GetMapping("/ai-preferences")
    public AiPreferencesDto getAiPreferences() {
        return settingsService.getAiPreferences();
    }
    @PutMapping("/ai-preferences")
    public AiPreferencesDto updateAiPreferences(
            @RequestBody AiPreferencesDto dto) {

        return settingsService.updateAiPreferences(dto);
    }

    @GetMapping("/restaurant")
    public RestaurantPreferencesDto getRestaurant() {
        return settingsService.getRestaurant();
    }
    @PutMapping("/restaurant")
    public RestaurantPreferencesDto updateRestaurant(
            @RequestBody RestaurantPreferencesDto dto) {

        return settingsService.updateRestaurant(dto);
    }

    @GetMapping("/application")
    public ApplicationPreferencesDto getApplication() {
        return settingsService.getApplication();
    }
    @PutMapping("/application")
    public ApplicationPreferencesDto updateApplication(
            @RequestBody ApplicationPreferencesDto dto) {

        return settingsService.updateApplication(dto);
    }

    @GetMapping("/about")
    public AboutDto getAbout() {
        return settingsService.getAbout();
    }

    @GetMapping("/system-status")
    public SystemStatusDto getSystemStatus() {
        return settingsService.getSystemStatus();
    }

}