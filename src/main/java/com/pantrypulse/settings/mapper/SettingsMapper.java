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

	public static AiPreferencesDto toAiPreferencesDto(Settings settings) {

		return AiPreferencesDto.builder().enableAiMenuPlanner(settings.getEnableAiMenuPlanner())
				.enableAiAssistant(settings.getEnableAiAssistant()).defaultCuisine(settings.getDefaultCuisine())
				.menuGenerationFrequency(settings.getMenuGenerationFrequency()).build();
	}

	public static void updateAiPreferences(Settings settings, AiPreferencesDto dto) {

		settings.setEnableAiMenuPlanner(dto.getEnableAiMenuPlanner());
		settings.setEnableAiAssistant(dto.getEnableAiAssistant());
		settings.setDefaultCuisine(dto.getDefaultCuisine());
		settings.setMenuGenerationFrequency(dto.getMenuGenerationFrequency());

	}

	public static RestaurantPreferencesDto toRestaurantDto(Settings settings) {

		return RestaurantPreferencesDto.builder().restaurantName(settings.getRestaurantName())
				.gstNumber(settings.getGstNumber()).primaryContactEmail(settings.getPrimaryContactEmail())
				.primaryPhone(settings.getPrimaryPhone()).address(settings.getAddress()).build();
	}

	public static void updateRestaurant(Settings settings, RestaurantPreferencesDto dto) {

		settings.setRestaurantName(dto.getRestaurantName());
		settings.setGstNumber(dto.getGstNumber());
		settings.setPrimaryContactEmail(dto.getPrimaryContactEmail());
		settings.setPrimaryPhone(dto.getPrimaryPhone());
		settings.setAddress(dto.getAddress());

	}

	public static ApplicationPreferencesDto toApplicationDto(Settings settings) {

		return ApplicationPreferencesDto.builder().language(settings.getLanguage()).currency(settings.getCurrency())
				.timeZone(settings.getTimeZone()).dateFormat(settings.getDateFormat()).build();
	}

	public static void updateApplication(Settings settings, ApplicationPreferencesDto dto) {

		settings.setLanguage(dto.getLanguage());
		settings.setCurrency(dto.getCurrency());
		settings.setTimeZone(dto.getTimeZone());
		settings.setDateFormat(dto.getDateFormat());

	}
}