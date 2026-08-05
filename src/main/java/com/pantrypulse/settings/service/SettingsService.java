package com.pantrypulse.settings.service;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.authentication.repository.UserRepository;
import com.pantrypulse.authentication.service.AuthenticatedUserService;
import com.pantrypulse.settings.dto.AboutDto;
import com.pantrypulse.settings.dto.ChangePasswordRequest;
import com.pantrypulse.settings.dto.NotificationSettingsDto;
import com.pantrypulse.settings.dto.ProfileDto;
import com.pantrypulse.settings.entity.Settings;
import com.pantrypulse.settings.mapper.SettingsMapper;
import com.pantrypulse.settings.repository.SettingsRepository;
import com.pantrypulse.exception.InvalidPasswordException;

import lombok.RequiredArgsConstructor;
@Service
@RequiredArgsConstructor
public class SettingsService {

    
    private final AuthenticatedUserService authenticatedUserService;
    private final SettingsRepository settingsRepository;
    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;
    private Settings getSettings() {

        User currentUser = authenticatedUserService.getCurrentUser();

        return settingsRepository.findByOwner(currentUser)
                .orElseGet(() -> {

                    Settings settings = new Settings();

                    settings.setOwner(currentUser);

                    // Required fields
                    settings.setFullName(currentUser.getName());
                    settings.setEmail(currentUser.getEmail());
                    settings.setRole(currentUser.getRole().name());

                    // Optional fields
                    settings.setPhoneNumber("");
                    settings.setRestaurantName("");
                    settings.setProfileImageUrl("");

                    // Default notification settings
                    settings.setLowStockAlerts(true);
                    settings.setExpiryAlerts(true);
                    settings.setAiMenuNotifications(true);
                    settings.setEmailNotifications(false);

                    return settingsRepository.save(settings);
                });
    }
    public void changePassword(ChangePasswordRequest request) {

        User currentUser = authenticatedUserService.getCurrentUser();

        if (!passwordEncoder.matches(
                request.getCurrentPassword(),
                currentUser.getPassword())) {

            throw new InvalidPasswordException(
                    "Current password is incorrect");
        }

        if (!request.getNewPassword()
                .equals(request.getConfirmPassword())) {

            throw new InvalidPasswordException(
                    "Passwords do not match");
        }

        currentUser.setPassword(
                passwordEncoder.encode(request.getNewPassword()));

        userRepository.save(currentUser);
    }
    public ProfileDto getProfile() {
        return SettingsMapper.toProfileDto(getSettings());
    }

    public ProfileDto updateProfile(ProfileDto dto) {

        Settings settings = getSettings();

        SettingsMapper.updateProfile(settings, dto);

        return SettingsMapper.toProfileDto(
                settingsRepository.save(settings));
    }

   
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

