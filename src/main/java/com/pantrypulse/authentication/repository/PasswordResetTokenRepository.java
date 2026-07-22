package com.pantrypulse.authentication.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

import com.pantrypulse.authentication.entity.PasswordResetToken;
import com.pantrypulse.authentication.entity.User;
public interface PasswordResetTokenRepository
extends JpaRepository<PasswordResetToken, Long>,JpaSpecificationExecutor<PasswordResetToken>  {

Optional<PasswordResetToken> findByToken(String token);

Optional<PasswordResetToken> findByUser(User user);

void deleteByUser(User user);
}