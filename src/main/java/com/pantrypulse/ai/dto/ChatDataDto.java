package com.pantrypulse.ai.dto;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

@Data
public class ChatDataDto {

    private String question;
    private String language;
    private Double confidence;
    private String answer;
    private List<String> sources;

    @JsonProperty("retrieved_chunks")
    private Integer retrievedChunks;

    private String provider;

    @JsonProperty("fallback_used")
    private Boolean fallbackUsed;

    @JsonProperty("response_time_ms")
    private Integer responseTimeMs;
}