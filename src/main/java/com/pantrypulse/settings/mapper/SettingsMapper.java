package com.pantrypulse.settings.mapper;

import com.pantrypulse.settings.dto.*;
import com.pantrypulse.settings.entity.Settings;

public class SettingsMapper {

	private SettingsMapper() {
	}

	public static ProfileDto toProfileDto(Settings settings) {

		return ProfileDto.builder().id(settings.getId()).fullName(settings.getFullName()).email(settings.getEmail())
				.phoneNumber(settings.getPhoneNumber()).role(settings.getRole())
				.restaurantName(settings.getRestaurantName()).profileImageUrl(settings.getProfileImageUrl()).build();
	}

	public static void updateProfile(Settings settings, ProfileDto dto) {

	    settings.setFullName(dto.getFullName());
	    settings.setPhoneNumber(dto.getPhoneNumber());
	    settings.setRestaurantName(dto.getRestaurantName());
	    settings.setRole(dto.getRole());

	}

	public static NotificationSettingsDto toNotificationDto(Settings settings) {

		return NotificationSettingsDto.builder().lowStockAlerts(settings.getLowStockAlerts())
				.expiryAlerts(settings.getExpiryAlerts()).aiMenuNotifications(settings.getAiMenuNotifications())
				.emailNotifications(settings.getEmailNotifications()).build();
	}

	public static void updateNotifications(Settings settings, NotificationSettingsDto dto) {

		settings.setLowStockAlerts(dto.getLowStockAlerts());
		settings.setExpiryAlerts(dto.getExpiryAlerts());
		settings.setAiMenuNotifications(dto.getAiMenuNotifications());
		settings.setEmailNotifications(dto.getEmailNotifications());

	}
}