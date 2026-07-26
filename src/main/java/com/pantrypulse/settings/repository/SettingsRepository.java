package com.pantrypulse.settings.repository;

import com.pantrypulse.settings.entity.Settings;
import org.springframework.data.jpa.repository.JpaRepository;
import com.pantrypulse.authentication.entity.User;
import java.util.Optional;
public interface SettingsRepository extends JpaRepository<Settings, Long> {

    Optional<Settings> findByOwner(User owner);

}