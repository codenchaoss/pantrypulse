package com.pantrypulse.ai.client;

import java.time.Instant;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import com.pantrypulse.ai.dto.ChatRequestDto;
import com.pantrypulse.ai.dto.ChatResponseDto;
import com.pantrypulse.ai.dto.MenuRequestDto;
import com.pantrypulse.ai.dto.MenuResponseDto;
import com.pantrypulse.ai.dto.OptimizationRequestDto;
import com.pantrypulse.ai.dto.OptimizationResponseDto;
import com.pantrypulse.ai.dto.PricingRequestDto;
import com.pantrypulse.ai.dto.PricingResponseDto;
import com.pantrypulse.ai.dto.RecipeRequestDto;
import com.pantrypulse.ai.dto.RecipeResponseDto;
import com.pantrypulse.ai.dto.SupplierRequestDto;
import com.pantrypulse.ai.dto.SupplierResponseDto;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
@ConditionalOnProperty(
        name = "ai.enabled",
        havingValue = "true"
)
public class AiClient {

    private static final String AI_EMPTY_RESPONSE =
            "AI returned empty response.";

    private static final String AI_UNAVAILABLE =
            "AI service is currently unavailable. Please try again later.";

    private final RestTemplate restTemplate;

    @Value("${ai.service.url}")
    private String aiUrl;

    public AiClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public MenuResponseDto generateMenu(MenuRequestDto request) {

        log.info("Sending AI request to {}", aiUrl);

        long start = System.currentTimeMillis();

        try {

            MenuResponseDto response = restTemplate.postForObject(
                    aiUrl + "/menu",
                    request,
                    MenuResponseDto.class
            );

            long end = System.currentTimeMillis();

            log.info("AI menu generated in {} ms", (end - start));

            if (response == null) {
                return MenuResponseDto.builder()
                        .success(false)
                        .timestamp(Instant.now().toString())
                        .message(AI_EMPTY_RESPONSE)
                        .build();
            }

            return response;

        } catch (RestClientException ex) {

            log.error("AI service unavailable", ex);

            return MenuResponseDto.builder()
                    .success(false)
                    .timestamp(Instant.now().toString())
                    .message(AI_UNAVAILABLE)
                    .build();
        }
    }

    public ChatResponseDto chat(ChatRequestDto request) {

        log.info("Sending Chat AI request to {}", aiUrl);

        long start = System.currentTimeMillis();

        try {

            ChatResponseDto response = restTemplate.postForObject(
                    aiUrl + "/chat",
                    request,
                    ChatResponseDto.class
            );

            long end = System.currentTimeMillis();

            log.info("AI chat completed in {} ms", (end - start));

            if (response == null) {
                return ChatResponseDto.builder()
                        .success(false)
                        .timestamp(Instant.now().toString())
                        .message(AI_EMPTY_RESPONSE)
                        .build();
            }

            return response;

        } catch (RestClientException ex) {

            long end = System.currentTimeMillis();

            log.error("AI chat failed after {} ms", (end - start), ex);

            return ChatResponseDto.builder()
                    .success(false)
                    .timestamp(Instant.now().toString())
                    .message(AI_UNAVAILABLE)
                    .build();
        }
    }

    public RecipeResponseDto recommendRecipe(RecipeRequestDto request) {

        log.info("Sending Recipe AI request to {}", aiUrl);

        try {

            RecipeResponseDto response = restTemplate.postForObject(
                    aiUrl + "/recipe",
                    request,
                    RecipeResponseDto.class
            );

            if (response == null) {

                RecipeResponseDto fallback = new RecipeResponseDto();

                fallback.setSuccess(false);
                fallback.setTimestamp(Instant.now().toString());

                return fallback;
            }

            return response;

        } catch (RestClientException ex) {

            log.error("Recipe AI service unavailable", ex);

            RecipeResponseDto fallback = new RecipeResponseDto();

            fallback.setSuccess(false);
            fallback.setTimestamp(Instant.now().toString());

            return fallback;
        }
    }

    public SupplierResponseDto generateSupplierMessage(
            SupplierRequestDto request) {

        log.info("Sending Supplier AI request to {}", aiUrl);

        try {

            SupplierResponseDto response = restTemplate.postForObject(
                    aiUrl + "/supplier",
                    request,
                    SupplierResponseDto.class
            );

            if (response == null) {

                SupplierResponseDto fallback =
                        new SupplierResponseDto();

                fallback.setSuccess(false);
                fallback.setTimestamp(Instant.now().toString());
                fallback.setMessage(AI_EMPTY_RESPONSE);

                return fallback;
            }

            return response;

        } catch (RestClientException ex) {

            log.error("Supplier AI service unavailable", ex);

            SupplierResponseDto fallback =
                    new SupplierResponseDto();

            fallback.setSuccess(false);
            fallback.setTimestamp(Instant.now().toString());
            fallback.setMessage(AI_EMPTY_RESPONSE);

            return fallback;
        }
    }

    public PricingResponseDto suggestPricing(
            PricingRequestDto request) {

        log.info("Sending Pricing AI request to {}", aiUrl);

        try {

            PricingResponseDto response = restTemplate.postForObject(
                    aiUrl + "/pricing",
                    request,
                    PricingResponseDto.class
            );

            if (response == null) {

                PricingResponseDto fallback =
                        new PricingResponseDto();

                fallback.setSuccess(false);
                fallback.setTimestamp(Instant.now().toString());
                fallback.setMessage(AI_EMPTY_RESPONSE);

                return fallback;
            }

            return response;

        } catch (RestClientException ex) {

            log.error("Pricing AI service unavailable", ex);

            PricingResponseDto fallback =
                    new PricingResponseDto();

            fallback.setSuccess(false);
            fallback.setTimestamp(Instant.now().toString());
            fallback.setMessage(AI_EMPTY_RESPONSE);

            return fallback;
        }
    }

    public OptimizationResponseDto optimizeInventory(
            OptimizationRequestDto request) {

        log.info("Sending Optimization AI request to {}", aiUrl);

        try {

            OptimizationResponseDto response =
                    restTemplate.postForObject(
                            aiUrl + "/optimization",
                            request,
                            OptimizationResponseDto.class
                    );

            if (response == null) {

                OptimizationResponseDto fallback =
                        new OptimizationResponseDto();

                fallback.setSuccess(false);
                fallback.setTimestamp(Instant.now().toString());
                fallback.setMessage(AI_EMPTY_RESPONSE);

                return fallback;
            }

            return response;

        } catch (RestClientException ex) {

            log.error("Optimization AI failed", ex);

            OptimizationResponseDto fallback =
                    new OptimizationResponseDto();

            fallback.setSuccess(false);
            fallback.setTimestamp(Instant.now().toString());
            fallback.setMessage(AI_UNAVAILABLE);

            return fallback;
        }
    }
}