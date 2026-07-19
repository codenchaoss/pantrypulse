package com.pantrypulse.settings.repository;

import com.pantrypulse.settings.entity.Settings;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SettingsRepository extends JpaRepository<Settings, Long> {

}