package com.pantrypulse.settings.service;

import org.springframework.stereotype.Service;

import com.pantrypulse.settings.dto.AboutDto;
import com.pantrypulse.settings.dto.NotificationSettingsDto;
import com.pantrypulse.settings.dto.ProfileDto;
import com.pantrypulse.settings.entity.Settings;
import com.pantrypulse.settings.mapper.SettingsMapper;
import com.pantrypulse.settings.repository.SettingsRepository;

import lombok.RequiredArgsConstructor;
@Service
@RequiredArgsConstructor
public class SettingsService {

    private final SettingsRepository settingsRepository;

    private Settings getSettings() {

        return settingsRepository.findById(1L)
                .orElseThrow(() ->
                        new RuntimeException("Settings not found."));
    }

    // PROFILE

    public ProfileDto getProfile() {
        return SettingsMapper.toProfileDto(getSettings());
    }

    public ProfileDto updateProfile(ProfileDto dto) {

        Settings settings = getSettings();

        SettingsMapper.updateProfile(settings, dto);

        return SettingsMapper.toProfileDto(
                settingsRepository.save(settings));
    }

    // NOTIFICATIONS

    public NotificationSettingsDto getNotifications() {

        return SettingsMapper.toNotificationDto(getSettings());
    }

    public NotificationSettingsDto updateNotifications(NotificationSettingsDto dto) {

        Settings settings = getSettings();

        SettingsMapper.updateNotifications(settings, dto);

        return SettingsMapper.toNotificationDto(
                settingsRepository.save(settings));
    }


    public AboutDto getAbout() {

        return AboutDto.builder()
                .application("PantryPulse")
                .frontendVersion("1.0.0")
                .backendVersion("1.0.0")
                .angularVersion("20")
                .springBootVersion("3.5.3")
                .database("MySQL")
                .build();
    }
}

