package com.pantrypulse.ai.service;

import java.util.List;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import com.pantrypulse.ai.client.AiClient;
import com.pantrypulse.ai.dto.SupplierRequestDto;
import com.pantrypulse.ai.dto.SupplierResponseDto;
import com.pantrypulse.authentication.entity.User;
import com.pantrypulse.authentication.service.AuthenticatedUserService;
import com.pantrypulse.supplier.entity.Supplier;
import com.pantrypulse.supplier.repository.SupplierRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
@Slf4j
@Service
@RequiredArgsConstructor
@ConditionalOnProperty(
	    name = "ai.enabled",
	    havingValue = "true"
	)
public class SupplierAiService {

    private final AiClient aiClient;
    private final SupplierRepository supplierRepository;
    private final AuthenticatedUserService authenticatedUserService;

    public SupplierResponseDto generateSupplierMessage(
            SupplierRequestDto request) {

        User user = authenticatedUserService.getCurrentUser();

        List<Supplier> suppliers = supplierRepository.findByOwner(user);

        log.info("Found {} suppliers for user {}",
                suppliers.size(),
                user.getId());


        return aiClient.generateSupplierMessage(request);

    }
    
}