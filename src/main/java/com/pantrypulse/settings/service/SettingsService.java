package com.pantrypulse.settings.service;

import com.pantrypulse.settings.dto.*;
import com.pantrypulse.settings.entity.Settings;
import com.pantrypulse.settings.mapper.SettingsMapper;
import com.pantrypulse.settings.repository.SettingsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class SettingsService {

    private final SettingsRepository settingsRepository;
    private Settings getSettings() {

        return settingsRepository.findById(1L)
                .orElseThrow(() ->
                        new RuntimeException("Settings not found."));
    }

    public ProfileDto getProfile() {

        return SettingsMapper.toProfileDto(getSettings());
    }
    public ProfileDto updateProfile(ProfileDto dto) {

        Settings settings = getSettings();

        SettingsMapper.updateProfile(settings, dto);

        Settings updated = settingsRepository.save(settings);

        return SettingsMapper.toProfileDto(updated);
    }

    public NotificationSettingsDto getNotifications() {

        return SettingsMapper.toNotificationDto(getSettings());
    }
    public NotificationSettingsDto updateNotifications(NotificationSettingsDto dto) {

        Settings settings = getSettings();

        SettingsMapper.updateNotifications(settings, dto);

        Settings updated = settingsRepository.save(settings);

        return SettingsMapper.toNotificationDto(updated);
    }

    public AiPreferencesDto getAiPreferences() {

        return SettingsMapper.toAiPreferencesDto(getSettings());
    }
    public AiPreferencesDto updateAiPreferences(AiPreferencesDto dto) {

        Settings settings = getSettings();

        SettingsMapper.updateAiPreferences(settings, dto);

        Settings updated = settingsRepository.save(settings);

        return SettingsMapper.toAiPreferencesDto(updated);
    }

    public RestaurantPreferencesDto getRestaurant() {

        return SettingsMapper.toRestaurantDto(getSettings());
    }
    public RestaurantPreferencesDto updateRestaurant(RestaurantPreferencesDto dto) {

        Settings settings = getSettings();

        SettingsMapper.updateRestaurant(settings, dto);

        Settings updated = settingsRepository.save(settings);

        return SettingsMapper.toRestaurantDto(updated);
    }

    public ApplicationPreferencesDto getApplication() {

        return SettingsMapper.toApplicationDto(getSettings());
    }
    public ApplicationPreferencesDto updateApplication(ApplicationPreferencesDto dto) {

        Settings settings = getSettings();

        SettingsMapper.updateApplication(settings, dto);

        Settings updated = settingsRepository.save(settings);

        return SettingsMapper.toApplicationDto(updated);
    }

    public AboutDto getAbout() {

        return AboutDto.builder()
                .application("KitchenSync AI (PantryPulse)")
                .systemVersion("1.0")
                .frontendVersion("1.0.0")
                .backendVersion("1.0.0")
                .angularVersion("20")
                .springBootVersion("3.5.3")
                .database("MySQL")
                .build();
    }
    public SystemStatusDto getSystemStatus() {

        return SystemStatusDto.builder()
                .backend("ONLINE")
                .database("ONLINE")
                .aiService("ONLINE")
                .build();
    }

}